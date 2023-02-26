from Cryptodome.PublicKey import RSA
from Cryptodome.Util import number
from bs4 import BeautifulSoup
import datetime
import requests
import argparse
import logging
import mpmath
import time


from . import __version__
from .utils import init_logger

FACTOR_DB_URL = "http://factordb.com/index.php"

_logger = init_logger(__name__, logging.INFO)


class FactorDBError(Exception):
    pass


class FactorDB:
    @staticmethod
    def _get_int_href(href) -> int:
        nid = href.get("href").split("=")[1].strip("/")
        response = requests.get(FACTOR_DB_URL, params={"showid": nid})
        soup = BeautifulSoup(response.text, "html.parser")
        number = (
            soup.findAll("table")[1]
            .findAll("tr")[2]
            .findAll("td")[1]
            .get_text()
            .replace("\r\n", "")
            .replace("\n", "")
            .strip()
        )
        number = int(number)
        return number

    @staticmethod
    def factorize(n) -> list:
        try:
            response = requests.get(FACTOR_DB_URL, params={"query": n})
            soup = BeautifulSoup(response.text, "html.parser")
        except:
            raise FactorDBError("Network connection failed.")

        try:
            factors = (
                soup.findAll("table")[1].findAll("tr")[2].findAll("td")[2].findAll("a")
            )
        except:
            raise FactorDBError(
                "Failed to parse data. Maybe the HTML of FactorDB has changed."
            )
        if len(factors) != 3:
            raise FactorDBError(
                "Factorization not found on FactorDB or n is not semiprime."
            )

        factors = list(map(FactorDB._get_int_href, factors))
        factors.remove(int(n))
        return factors


class WeakPrimesFactorizer:
    def __init__(self):
        mpmath.mp.dps = 1235

    def __is_square(self, number):
        sqrt = mpmath.sqrt(number)
        return mpmath.floor(sqrt) == mpmath.ceil(sqrt)

    def __print_progress(self, attempts, start_time):
        string = "Attempts: {} Time: {}".format(
            attempts, datetime.timedelta(seconds=int(time.time() - start_time))
        )
        _logger.info(string)

    def factorize(self, n):
        start_time = time.time()
        attempts = 1
        a = mpmath.ceil(mpmath.sqrt(n))
        b_sq = a * a - n
        while not self.__is_square(b_sq):
            a += 1
            attempts += 1
            if attempts % 100000 == 0:
                self.__print_progress(attempts, start_time)
            b_sq = a * a - n
        self.__print_progress(attempts, start_time)
        _logger.info("Done!")

        b = mpmath.sqrt(b_sq)
        p = a + b
        q = a - b
        return int(p), int(q)


class RSAGen:
    def __init__(self, p, q, n, e=0x10001):
        if p < q:
            p, q = q, p  # OpenSSL
        self.n = n or p * q
        self.e = e
        self.p = p
        self.q = q

    @staticmethod
    def __calculate_d(e, p, q) -> int:
        return number.inverse(e, (p - 1) * (q - 1))

    def gen_private(self, save_path=None):
        d = self.__calculate_d(self.e, self.p, self.q)
        key = RSA.construct((self.n, self.e, d, self.p, self.q))
        self.print_or_save(key, save_path)

    def gen_public(self, save_path=None):
        key = RSA.construct((self.n, self.e))
        self.print_or_save(key, save_path)

    @staticmethod
    def print_or_save(key, path=None):
        key = key.exportKey(format="PEM")
        if not isinstance(key, str):
            key = key.decode("utf-8")
        if not path:
            print()
            print(key)
        else:
            with open(path, "w") as f:
                f.write(key)


class Pwn:
    def __init__(self, args):
        if args.silent:
            _logger.setLevel(logging.WARNING)
        self.__args = args
        self.__wpf = WeakPrimesFactorizer()

    @staticmethod
    def __resolve_pqne(args) -> tuple:
        if not args.n and args.p and args.q:
            return int(args.p), int(args.q), int(args.p) * int(args.q), int(args.e)
        elif args.n and args.p and not args.q:
            return int(args.p), int(args.n) // int(args.p), int(args.n), int(args.e)
        elif args.n and not args.p and args.q:
            return int(args.n) // int(args.q), int(args.q), int(args.n), int(args.e)
        elif args.n:
            return None, None, int(args.n), int(args.e)

    def gen_from_value(self, pqne=None):
        p, q, n, e = pqne or self.__resolve_pqne(self.__args)
        if self.__args.gen_pub:
            RSAGen(p, q, n, e).gen_public(self.__args.save_path)
            return
        if not p and not q:
            _logger.info("Getting factors from factorDB.com ...")
            try:
                pq = FactorDB.factorize(n)
            except FactorDBError as err:
                if not self.__args.weak:
                    _logger.error(err)
                    exit(1)
                _logger.info(err)
                _logger.info("Trying weak primes factorization...")
                pq = self.__wpf.factorize(n)
            if not pq:
                return
            p, q = pq
        RSAGen(p, q, n, e).gen_private(self.__args.save_path)

    def gen_from_key(self):
        with open(self.__args.pub_key, "r") as f:
            key = RSA.import_key(f.read())
        if self.__args.gen_pub:
            RSAGen.print_or_save(key.publickey(), self.__args.save_path)
        elif key.has_private():
            RSAGen.print_or_save(key, self.__args.save_path)
        else:
            self.gen_from_value((None, None, key.n, key.e))

    def run(self):
        if self.__args.pub_key:
            self.gen_from_key()
        elif self.__resolve_pqne(self.__args):
            self.gen_from_value()
        else:
            _logger.error(
                "Invalid argument combination.\nYou must provide either n or a key.\nTry -h for help."
            )
            exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Genarate private key from public key using FactorDB.com or p, q"
    )
    parser.add_argument(
        "-k",
        "--key",
        dest="pub_key",
        metavar="PATH",
        help="Try generating from key file.",
    )
    parser.add_argument(
        "-x",
        "--gen-public",
        dest="gen_pub",
        action="store_true",
        help="Genarate public key file insted of private.",
    )
    parser.add_argument(
        "-o",
        "--out",
        dest="save_path",
        metavar="PATH",
        help="Save key into a file instead of printing.",
    )
    parser.add_argument(
        "-w",
        "--weak",
        dest="weak",
        action="store_true",
        help="Use Fermat's Factorization Algorithm. If factorDB.com fails.",
    )
    parser.add_argument(
        "-s", "--silent", dest="silent", action="store_true", help="Silent mode."
    )
    parser.add_argument(
        "-p", dest="p", metavar="VALUE", help="1st prime value of RSA key."
    )
    parser.add_argument(
        "-q", dest="q", metavar="VALUE", help="2nd prime value of RSA key."
    )
    parser.add_argument("-n", dest="n", metavar="VALUE", help="n value of RSA key.")
    parser.add_argument(
        "-e",
        dest="e",
        metavar="VALUE",
        help="Public exponent value of RSA key.",
        default="65537",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="v" + str(__version__)
    )

    args = parser.parse_args()
    pwn = Pwn(args)
    pwn.run()


if __name__ == "__main__":
    main()
