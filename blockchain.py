#coding: utf-8
import time
import hashlib
import platform
import json
import os
import glob
from config import NODES
import requests

NUM_ZEROS = 6
WINDOWS_DATA_DIR = 'D:\\blockchain\\'
UNIX_DATA_DIR = '/tmp/blockchain'

def get_platform():
    return platform.system().lower()

def get_data_dir():
    if get_platform() == 'windows':
        return WINDOWS_DATA_DIR
    return UNIX_DATA_DIR

class Block(object):

    def _calc_hash(self, data, nonce, prev_hash):
        return hashlib.sha256(data + str(nonce) + prev_hash).hexdigest()

    def __init__(self, **kwargs):
        self.id = int(kwargs['id'])
        self.prev_hash = kwargs['prev_hash']
        self.nonce = int(kwargs['nonce'])
        self.data = kwargs['data']
        self.timestamp = int(kwargs['timestamp'])
        self.hash = self._calc_hash(self.data, self.nonce, self.prev_hash)

    def store_block(self):
        DIR = get_data_dir()
        if not os.path.exists(DIR):
            os.mkdir(DIR)
        fp = os.path.join(DIR, str(self.id).zfill(6) + '.json')
        if os.path.exists(fp):
            return False
        with open(fp, 'w') as f:
            json.dump(self.__dict__, f)
        return True

class ProofOfWork(object):
    def __init__(self, block, prev_block):
        self.block = block
        self.prev_block = prev_block
        self.target_max = self._calc_target_max()
        self.difficulty = self._get_difficulty()
        self.target = self._calc_target()

    def _calc_target_max(self):
        return ('1' + '0' * (64 - NUM_ZEROS)).zfill(64)

    def _get_difficulty(self):
        return 1

    def _calc_target(self):
        int_max = int(self.target_max, 16)
        target = int_max / self.difficulty
        hex_target = hex(target)
        if hex_target.startswith('0x'):
            hex_target = hex_target[2:]
        return hex_target.zfill(64)

    def is_block_valid(self):
        return self.block and self.block.hash and self.block.hash < self.target and self.block.hash.startswith('0' * NUM_ZEROS) and self.block.id == self.prev_block.id + 1 and self.block.prev_hash == self.prev_block.hash

class BlockChain(object):
    def __init__(self):
        self._initial_chain()

    def _initial_chain(self):
        DIR = get_data_dir()
        self.blocks = []
        if os.path.exists(DIR):
            for file in sorted(glob.glob(os.path.join(DIR, '*.json'))):
                with open(file) as fp:
                    block = Block(**json.load(fp))
                    self.blocks.append(block)


    def create_genesis_block(self):
        params = {
            'id': 0,
            'data': '',
            'nonce': 0,
            'prev_hash': '',
            'timestamp': int(time.time())
        }
        genesis_block = Block(**params)
        self.blocks.append(genesis_block)
        genesis_block.store_block()
        return True

    def add_block(self, block):
        if not ProofOfWork(block, self.get_last_block()).is_block_valid():
            return False
        self.blocks.append(block)
        block.store_block()
        return True

    def broadcast(self, block):
        for node in NODES:
            try:
                requests.post(node + '/add_block', data = block.__dict__, timeout=10)
            except requests.exceptions.ConnectionError:
                print 'broadcast to {} failed.'.format(node)

    def store_chain(self):
        for block in self.blocks:
            block.store_block()

    def get_last_block(self):
        return self.blocks[-1]

    def chain_to_json(self):
        result = []
        for block in self.blocks:
            result.append(block.__dict__)
        return json.dumps(result)

    def is_chain_valid(self):
        prev_block = self.blocks[0]
        for block in self.blocks[1:]:
            if not ProofOfWork(block, prev_block).is_block_valid():
                return False
            prev_block = block
        return True


#目的是要根据blockchain中的最后一个block，找到一个符合条件的新的block
def mine(prev_block):
    nonce = 0
    while True:
        data = 'block ' + str(prev_block.id + 1)
        params = {
            'id': prev_block.id + 1,
            'data': data,
            'nonce': nonce,
            'prev_hash': prev_block.hash,
            'timestamp': int(time.time())
        }
        block = Block(**params)
        if ProofOfWork(block, prev_block).is_block_valid():
            return block
        nonce += 1

def sync():
    for node in NODES:
        url = node + '/chain.json'
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.ConnectionError:
            print 'sync error:server may not be running.'
            return False
        else:
            try:
                blocks = json.loads(response._content)
            except ValueError:
                print 'sync error:JSON decoded error.'
                return False
            else:
                for item in blocks:
                    block = Block(**item)
                    block.store_block()
                return True
    return False
