from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from argparse import ArgumentParser
import requests
import os
from . import __version__

FACTOR_DB_URL = 'http://factordb.com/index.php'

def get_int_href(href) -> int:
    nid = href.get('href').split('=')[1].strip('/')
    response = requests.get(FACTOR_DB_URL, params = {'showid': nid})
    soup = BeautifulSoup(response.text, 'html.parser')
    number = soup.findAll('table')[1].findAll('tr')[2].findAll('td')[1].get_text().replace(os.linesep, '').replace('\n','')
    number = int(number)
    return number

def factor_db(n) -> list:
    try:
        response = requests.get(FACTOR_DB_URL, params = {'query': n})
        soup = BeautifulSoup(response.text, 'html.parser')
    except:
        print('Network connection failed.')
        return

    try:
        factors = soup.findAll('table')[1].findAll('tr')[2].findAll('td')[2].findAll('a')
    except:
        print('Failed to parse data. Maybe the HTML of FactorDB has changed.')
        return

    if(len(factors) != 3):
        print('Factorization not found on FactorDB or n is not semiprime.')
        return
    
    factors = list(map(get_int_href, factors))
    factors.remove(int(n))
    return factors

def calculate_d(e, p, q) -> int:
    # Modified method from: https://stackoverflow.com/questions/23279208/calculate-d-from-n-e-p-q-in-rsa
    # Answer by: https://stackoverflow.com/users/448810/user448810
    
    m = (p-1)*(q-1)
    a, b, u = 0, m, 1
    while e > 0:
        q = b // e # integer division
        e, a, b, u = b % e, u, e, a - q * u
    if b == 1:
        return a % m
    raise ValueError("Must be coprime.")

def print_or_save(key, path=None):
    key = key.exportKey(format='PEM')
    if(not isinstance(key,str)):
        key = key.decode('utf-8')
    if(not path):
        print()
        print(key)
    else:
        with open(path,'w') as f:
            f.write(key)

def gen_private(p, q, n=None, e = 0x10001, save_path=None):
    if(p<q):
        p,q = q,p # OpenSSL
    if(not n):
        n = p * q
    d = calculate_d(e,p,q)
    key = RSA.construct((n,e,d,p,q))
    print_or_save(key, save_path)

def gen_public(n, e=0x10001, save_path = None):
    key = RSA.construct((n,e))
    print_or_save(key, save_path)

def resolve_pqne(args)->tuple:
    if(not args.n and args.p and args.q):
        return int(args.p), int(args.q), int(args.p) * int(args.q), int(args.e)
    elif(args.n and args.p and not args.q):
        return int(args.p), int(args.n) // int(args.p), int(args.n), int(args.e)
    elif(args.n and not args.p and args.q):
        return int(args.n) // int(args.q), int(args.q), int(args.n), int(args.e)
    elif(args.n):
        return None, None, int(args.n), int(args.e)

def gen_from_value(pqne, pub_key=False, save_path=None):
    p, q, n, e = pqne
    if(pub_key):
        gen_public(n, e, save_path)
        return
    if(not p and not q):
        print('Getting factors from factorDB.com ...')
        pq = factor_db(n)
        if(not pq):
            return
        p, q = pq
    gen_private(p,q,n,e,save_path)

def gen_from_key(key_path, pub_key=False, save_path=None):
    with open(key_path,'r') as f:
        key = RSA.import_key(f.read())
    if(pub_key):
        print_or_save(key.publickey(), save_path)
    elif(key.has_private()):
        print_or_save(key, save_path)
    else:
        gen_from_value((None, None, key.n, key.e), save_path=save_path)

def main():
    parser = ArgumentParser(description='Genarate private key from public key using FactorDB.com or p, q')
    parser.add_argument('-k','--key', dest='key', metavar='PATH', help='Try generating from key file.')
    parser.add_argument('-x','--gen-public', dest='gen_pub', action='store_true',help='Genarate public key file insted of private.')
    parser.add_argument('-o','--out', dest='out_path', metavar='PATH', help='Save key into a file instead of printing.')
    parser.add_argument('-p', dest='p', metavar='VALUE',help='1st prime value of RSA key.')
    parser.add_argument('-q', dest='q', metavar='VALUE',help='2nd prime value of RSA key.')
    parser.add_argument('-n', dest='n', metavar='VALUE',help='n value of RSA key.')
    parser.add_argument('-e', dest='e', metavar='VALUE',help='Public exponent value of RSA key.', default='65537')
    parser.add_argument('-v','--version',action='version',version='v'+str(__version__))

    args = parser.parse_args()
    if(args.key):
        gen_from_key(args.key, args.gen_pub, args.out_path)
        return
    
    pqne = resolve_pqne(args)
    if(pqne == None):
        print('Invalid argument combination.\nYou must provide either n or a key.\n')
        parser.print_usage()
        return
    
    gen_from_value(pqne, args.gen_pub, args.out_path)

if __name__ == "__main__":
    main()
