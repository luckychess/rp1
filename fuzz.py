#!/usr/bin/python

import subprocess
import os
import math
import random
import time
import json

fuzz_factor = 250
tries = 1200
counters = {"total": 0, "alive": 0, "crash": 0}
iroha_home = os.environ["IROHA_HOME"]
base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def get_fuzz_count(data_len):
    return random.randrange(math.ceil((float(data_len) / fuzz_factor))) + 1


def read_binary_data(file):
    return bytearray(open(file, "rb").read())


def read_json_data(file):
    data = json.load(open(file, "r"))
    return data


def fuzz_binary(fuzz_count, original_data):
    mod_data = original_data[:]
    for j in range(fuzz_count):
        random_byte = random.randrange(256)
        rn = random.randrange(len(original_data))
        mod_data[rn] = random_byte
    return mod_data


def fuzz_json(fuzz_count, original_data):
    keys = ["ip", "name", "publicKey", "privateKey"]
    mod_data = dict(original_data)
    for j in range(fuzz_count):
        me = random.randint(0, 1) == 0
        if me:
            selected_key = keys[random.randint(0, 3)]
            mod_data["me"][selected_key] = mod_value(selected_key, mod_data["me"][selected_key])
        else:
            selected_key = keys[random.randint(0, 2)]
            selected_group_member = random.randrange(len(mod_data["group"]))
            mod_data["group"][selected_group_member][selected_key] = \
                mod_value(selected_key, mod_data["group"][selected_group_member][selected_key])
    return mod_data


def mod_value(key, value):
    changed_value = list(value)
    if key == "ip":
        place = random.randrange(len(value))
        while value[place] == ".":
            place = random.randrange(len(value))
        changed_value[place] = chr(random.randint(0, 9) + 48)
    elif key == "name":
        place = random.randrange(len(value))
        changed_value[place] = chr(random.randrange(256))
    elif key == "publicKey" or key == "privateKey":
        place = random.randrange(len(value))
        while value[place] == "=":
            place = random.randrange(len(value))
        changed_value[place] = base64_chars[random.randrange(len(base64_chars))]
    return "".join(changed_value)


def black_box_fuzzer(filename, unfuzzed_data):
    current_config_file = open(filename, "wb")
    fuzzed_data = fuzz_binary(get_fuzz_count(len(unfuzzed_data)), unfuzzed_data)
    current_config_file.write(fuzzed_data)
    current_config_file.close()


def white_box_fuzzer(filename, unfuzzed_data):
    current_config_file = open(filename, "w")
    fuzzed_data = fuzz_json(get_fuzz_count(len(unfuzzed_data)), unfuzzed_data)
    current_config_file.write(json.dumps(fuzzed_data))
    current_config_file.close()


def run_activity():
    f = open("log.txt", "r+")

    process = subprocess.Popen([iroha_home + "/build/my_test_bin/sumeragi_test", "public"], stderr=f)
    time.sleep(3)

    counters["total"] += 1
    finished = process.poll()
    if not finished:
        process.terminate()
        counters["alive"] += 1
    else:
        if process.returncode != 0:
            f.seek(0)
            lines = f.readlines()
            print("crash detected")
            print(str(lines))
            crash_config_data = bytearray(open(iroha_home + "/config/sumeragi.json", "rb").read())
            open(iroha_home + "/config/crashcfg/sumeragi.json.crash" + str(counters["crash"]), "wb").write(
                crash_config_data)
            counters["crash"] += 1

    f.close()
    return counters


current_config_file_name = iroha_home + "/config/sumeragi.json"
reference_config_file_name = iroha_home + "/config/sumeragi.json.bak"


for i in range(0, tries):
    # black_box_fuzzer(current_config_file_name, reference_config_binary_data)
    # reference_config_binary_data = read_binary_data(reference_config_file_name)
    reference_config_json_data = read_json_data(reference_config_file_name)
    white_box_fuzzer(current_config_file_name, reference_config_json_data)
    run_activity()

print("Total runs: " + str(counters["total"]))
print("Alive: " + str(counters["alive"]))
print("Crashed: " + str(counters["crash"]))
