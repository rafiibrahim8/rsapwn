# rsapwn
#### Generate OpenSSL compilable private or public key form public key or RSA parameters. 

# INSTALLATION
From a command line enter the command to install rsapwn
```
$ pip install git+https://github.com/rafiibrahim8/rsapwn.git --upgrade
```
You need to have python 3 installed. I highly recommend to use a `virtualenv` for installation.

# USES

```bash
$ rsapwn [OPTIONS]
```
# OPTIONS
```
-h, --help           show this help message and exit
-k PATH, --key PATH  Try generating from key file.
-x, --gen-public     Generate public key file instead of private.
-o PATH, --out PATH  Save key into a file instead of printing.
-p VALUE             1st prime value of RSA key.
-q VALUE             2nd prime value of RSA key.
-n VALUE             n value of RSA key.
-e VALUE             Public exponent value of RSA key.
-v, --version        show program's version number and exit
```
You at least have to supply either a public key file or `n` of RSA for the program to work. 

# Example
```
rsapwn -k demo/id_rsa.pub
Getting factors from factorDB.com ...

-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCrX8mEDKC4SrP/TBPykumGWQkEL0qxTd55x8zOYAxgyI6XkYuX
btkQ8x1/GjLb38mMfMLWuTBRcmIPVIaI9TwAxFDdhhhUDTpFHpZHTMkE2g9ihVXZ
tepdzQjISXVzqnvGVKyaCRGB2oJGdr9VttNFb+1YZz49tqchEN1BPUp1twIDAQAB
AoGARp+y7DhIA6rFgvBXSCBDHJqUnKTgozDz/jvYqzPp5fjAyrWwUTfdPJ70CO1D
CFmxNbQ0l0i6INaCks7Coq5tizadZCsegBI8yxpf/v4xqG/NohLulILMw3maf7No
3tFgvy9GdzOvg69VXDXIni5tUOgKv2Jq9tDD170KNxLBQAECQQDY+qZVGCwhhBeJ
HFn65nVCW8LulVrN1/KrIlQ+Z1UgTlPkT5rdFm936igstSNq/1AbTrnxRsqTdY4Q
fzWvjEpBAkEAyjGQST2fkpDlLLn9abBzXsWnKpzv4RVkZip1uzOO0l8Iu4hPTZXY
dmAyzyaE4iobWJqa/+DD3ESaRc797uCR9wJBAI/OsGc9uiIMljy9mbV9AMKWZsAS
JTjAo4lhG0yw1+6te1Sanh1iPUbQ3weilnLX/JPcvch4DtNk2l98sGxFIwECQC9P
r6pjn/4kp2tyzcg4QJaxey8ub7bkUYzSbJ/0LXwuPpXbDGtkH7V7RwhPxBJDtghi
jNhI2Kum5c5l4+dMZvsCQB7+4DWeB1dBWtydif5Tq7TCCNCbMm5Kse8GJe3jC24b
Yj+Jy4wUQiTjxPzOpJz36m7ytDDfJszesT4G7kaCdc0=
-----END RSA PRIVATE KEY-----
```
```
rsapwn -n 135758287120038997506328099174252273287553619247783488775852850794420152322192587384247192398273827203767201272799289408983097530949963041115887584153551106773664915072101920711073273661561467417350689034268064998554331425491204471033772969010002776912424301263411797940417436136100939304329724586822878465001
Getting factors from factorDB.com ...

-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDBU4MHJ2F58q0BGkOZ4Q7+8kRt6IwSi/mI3LomtX8UrhFjDyRz
QIOtkEOOV2NwbquGiKt8X3z1Iv5Mrvp3ORZAXiN+/AySQNMawx15coHt+OF8K9k6
QHJrIQWWpxBopTinXaAVOavO1Tcaf6HNre+LHyVv5Dk2kddviQetAx2L6QIDAQAB
AoGAQSUnDg4TJsjDy49SIFRafUaeEHtAWC+a0qeugsS+IfXWHg9INR4UQTRPz3Nb
KtPgMOF1B+AVd3VnQ+fitrIh8M+sHb9RfTEMwzcCyDOaBg7fl+CREfvFYZSNJ9bd
Uild/itm9Hv4aM0sDbAGHMjssNPAbmUsfXrFfQNP5BRzGlECQQD8J2tBK7JaeQDw
Lk+H2YvdXmCXrj+Csk0ncTd3ZsTRgOfyYOba4G6qID5RxfoWqhu81g9OajljwPYg
pvQIgdIHAkEAxEZjoRs/HHD1GlGFMDseuUjiLD7LquLI9Y9n5zjEcHDy00jTu4VZ
tGww8I/dnh3czu/Jf5CL3Tu16MLwG2Z2jwJAZB6qwZe+G5pMOxHIVmKU3HLq248+
fICbjfuwUGKn55/NeTnssB/JERf4ZrO7V2B33wUH0tTusKMfl1tzLiWN5QJAO8uu
AqEIYyPOqEv5pa39ODmKHiyrY85fpuAfqYPT5OWkNNZVGyYPJDZp2oAZ5lf2s1y+
KIzi722Hh/gLqm1W5QJASW9jD/uLOXXdEgEsNM0S+ZPIFpFLMKJ0sqwJMiFUnLht
iYHCgJ7mkdmAZcQF+GkcJ3IvqOid2S7PFkIFrRQ51g==
-----END RSA PRIVATE KEY-----
```

# How does it work?
The program tries to find factor of  `n` from [FactorDB.com](http://factordb.com) the uses pythons [`pycryptodome`](https://github.com/Legrandin/pycryptodome/) to generate RSA private key. You can also generate public key from RSA parameters with this program.

# Acknowledgments
[user448810](https://stackoverflow.com/users/448810/user448810) for code of calculating `d`.
