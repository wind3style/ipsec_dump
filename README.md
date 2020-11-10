# ipsec_dump
IPsec ESP truffic dumper for Wireshark with saving keys which allows to decrypt ESP traffic dump on IPsec VPN local host.
It is usefull for:
* Capturing IP traffic of application if application works on hosts which is IPsec router.
* IP Monitoring of your's IPsec tunnels

## Instruction
* Place the files ipsec_dump.py and ipsec_dump_start_example.sh to linux OS with IPsec VPN
* Execute ./ipsec_dump_start_example.sh for collecting keys and ESP truffic dumping
* You will get files:
  * esp_sa - SA keys for Wireshark
  * pcap file - dump of IPsec ESP traffic.
* You should place esp_sa to Wireshark folder for example for Windows it is c:\Users\<User name>\AppData\Roaming\Wireshark>
* Start Wireshark and open pcap file
