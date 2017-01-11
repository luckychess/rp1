import requests
import random
import math
import subprocess
import os
import time

fuzz_count = 100
fuzz_factor = 250

iroha_home = os.environ["IROHA_HOME"]
address = "http://127.0.0.1:1204"
url_post = [address + "/account/register", address + "/asset/operation"]
request_data_post = [
    '{"publicKey":"WdvM/DPabapmtA7ISbTYPywbHxk8gWu2221LzmcmAgw=","alias":"yonezu","timestamp":1482053586}',
    '{"signature":"WdvM/DPabapmtA7ISbTYPywbHxk8gWu2221LzmcmAgw=","timestamp":1482053586, "asset-uuid":"21212121", "params":{"command":"add", "value":"12121212333", "sender":"me1", "receiver":"me2"}}']

url_get = ["http://127.0.0.1:1204/account", "http://127.0.0.1:1204/history/transaction"]


def fuzz_binary(fuzz_count, original_data):
    mod_data = original_data[:]
    for j in range(fuzz_count):
        random_byte = random.randrange(128)
        rn = random.randrange(len(original_data))
        mod_data[rn] = random_byte
    return mod_data


def get_fuzz_count(data_len):
    return random.randrange(math.ceil((float(data_len) / fuzz_factor))) + 1


logfile = open("full.log", "a")

for i in range(fuzz_count):
    query_index = random.randint(0, 1)
    bin_data_post = bytearray(request_data_post[query_index], "ascii")

    fuzzed_data = fuzz_binary(get_fuzz_count(len(bin_data_post)), bin_data_post)
    result_data = bytes(fuzzed_data).decode("ascii")

    r = "undefined"
    try:
        r = requests.post(url_post[query_index], data=result_data)

        logfile.write("fuzzed data: " + result_data)
        logfile.write("query: " + url_post[query_index])
        logfile.write("query result: " + r.content)
        logfile.write("\n")

        getres = requests.get(url_get)
        print(getres.content)

    except:
        process = subprocess.Popen([iroha_home + "/build/bin/iroha-main"])
        time.sleep(1)

logfile.close()
