#coding: utf-8
import argparse
from blockchain import Block, BlockChain, mine, sync

def main():
    parser = argparse.ArgumentParser(description="command line for operating blockchain")
    parser.add_argument('cmd', default='show_blockchain')

    args = parser.parse_args()
    if args.cmd == 'show_blockchain':
        chain = BlockChain()
        print chain.chain_to_json()
    elif args.cmd == 'mine':
        chain = BlockChain()
        block = mine(chain.get_last_block())
        print block.__dict__
        if chain.add_block(block):
            chain.broadcast(block)
    elif args.cmd == 'create_genesis':
        chain = BlockChain()
        if chain.create_genesis_block():
            print 'create genesis block succeed.'
        else:
            print 'create genesis block failed.'
    elif args.cmd == 'sync':
        if sync():
            print 'sync succeed.'
        else:
            print 'sync failed.'
    else:
        print 'Unknown command:{}'.format(args.cmd)

if __name__ == '__main__':
    main()