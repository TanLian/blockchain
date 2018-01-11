#coding: utf-8
from flask import Flask, jsonify, request
from blockchain import Block, BlockChain, mine, ProofOfWork, sync

app = Flask(__name__)

@app.route('/chain.json')
def get_chain():
    chain = BlockChain()
    return chain.chain_to_json()

@app.route('/add_block', methods=['POST'])
def add_block():
    block_dict = request.values.to_dict()
    block = Block(**block_dict)
    chain = BlockChain()
    last_block = chain.get_last_block()
    if ProofOfWork(block, last_block).is_block_valid():
        chain.add_block(block)

    return jsonify(received=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
