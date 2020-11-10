#!/usr/bin/python3

import subprocess
import re
import sys
import os

class ESP_SA:
    src = None
    dst = None
    spi = None
    auth_key = None
    auth_alg = None
    enc_key = None
    enc_alg = None

config_debug = False
config_output_file_name = "esp_sa"

def main(argv):
    print("IPSEC ESP truffic dumper for Wireshark with saving keys. Written by Fedorov Alexander <wind3style@gmail.com>\n")

    result = subprocess.run(['ip', 'xfrm', 'state'], stdout=subprocess.PIPE)
    esp_info = result.stdout.decode('utf-8')

    print_debug("esp_info:\n%s"%esp_info)
    esp_lines = esp_info.split("\n")
    
    SAs = ip_xfrm_parser(esp_lines)

        ### generate file 
    with open(config_output_file_name, "w") as fout:
        fout.write("# This file is automatically generated, DO NOT MODIFY.\r\n")
        for sa in SAs:
            fout.write('"IPv4","%s","%s","%s","%s","%s","%s","%s"\r\n'%(sa.src, sa.dst, sa.spi, sa.enc_alg, sa.enc_key, sa.auth_alg, sa.auth_key))

    cmd_exec = "tcpdump " + " ".join(argv[1:])
    print("cmd_exec: '%s'"%cmd_exec)
#    subprocess.run(["tcpdump"] + argv[1:])
    os.system(cmd_exec)


def print_debug(string):
    if config_debug:
        print(string)


def ip_xfrm_parser(esp_lines):
    
        ### list of ESP SA
    SAs = list()
        ### Parsing ESP SAa
    sa = ESP_SA()   ### First element
    for line in esp_lines:
        print_debug("line: %s"%line)
            ### example: src X1.X2.X3.X4 dst Y1.Y2.Y3,Y4
        match_ip = re.match(r'src ([\d\.]+) dst ([\d\.]+)', line)
        if match_ip:
            sa.src = match_ip.groups()[0]
            sa.dst = match_ip.groups()[1]
            print("src: %s, dst: %s"%(sa.src, sa.dst))

            ### example: proto esp spi 0x358bdb48 reqid 26 mode tunnel
        match_spi = re.match(r'\s*proto esp spi ([\S]+) ', line)
        if match_spi:
            sa.spi = match_spi.groups()[0]
            print("\tspi: %s"%(sa.spi))

            ### example: auth-trunc hmac(sha256) 0x006ead41d1c38efb02afeb05e98b70e3a2a59debc23cc9649e083a51f9249378 128
        match_auth = re.match(r'\s*auth-trunc ([\S]+) ([\S]+) ([\S]+)', line)
        if match_auth:
            sa.auth_key = match_auth.groups()[1]
            auth_alg1 = match_auth.groups()[0]
            auth_alg2 = match_auth.groups()[2]
            if auth_alg1 == 'hmac(sha256)' and auth_alg2 == "128":
                sa.auth_alg = "HMAC-SHA-256-128 [RFC4868]"
            elif auth_alg1 == 'hmac(sha256)' and auth_alg2 == "96":
                sa.auth_alg = "HMAC-SHA-256-96 [draft-ietf-ipsec-ciph-sha-256-00]"
            elif auth_alg1 == 'hmac(sha384)' and auth_alg2 == "192":
                sa.auth_alg = "HMAC-SHA-384-192 [RFC4868]"
            elif auth_alg1 == 'hmac(sha512)' and auth_alg2 == "256":
                sa.auth_alg = "HMAC-SHA-512-256 [RFC4868]"
            else:
                print("Unknow auth algorithm")
                sys.exit(1)
            print("\tauth_key: %s, auth_alg: %s"%(sa.auth_key, sa.auth_alg))

            ### example: enc cbc(aes) 0x4d79e6aa3f6f302d735f8eb1ec9ff1e79f89eff017b809420c7cf954e5ad9dee
        match_enc = re.match(r'\s*enc ([\S]+) ([\S]+)', line)
        if match_enc:
            enc_alg = match_enc.groups()[0]
            sa.enc_key = match_enc.groups()[1]
            if enc_alg == "cbc(aes)":
                sa.enc_alg = "AES-CBC [RFC3602]"
            print("\tenc_key: %s, enc_alg: %s"%(sa.enc_key, sa.enc_alg))

                ### last line
            SAs.append(sa)
            sa = ESP_SA()
    return SAs


if __name__ == "__main__":
    main(sys.argv)