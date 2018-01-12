#coding: utf-8
import argparse
import sys
from blockchain import BlockChain, mine, sync

def handle_show_chain_commands():
    chain = BlockChain()
    print chain.chain_to_json()

def mine_block():
    chain = BlockChain()
    block = mine(chain.get_last_block())
    print block.__dict__
    if chain.add_block(block):
        chain.broadcast(block)

def create_genesis():
    chain = BlockChain()
    if chain.create_genesis_block():
        print 'create genesis block succeed.'
    else:
        print 'create genesis block failed.'

def sync_nodes():
    if sync():
        print 'sync succeed.'
    else:
        print 'sync failed.'

def main():
    parser = argparse.ArgumentParser(description="command line for operating blockchain")
    subparsers = parser.add_subparsers(title='subcommands', description='')

    parser_show_chain = subparsers.add_parser('show_chain', help='print chain in json format.')
    parser_show_chain.set_defaults(func=handle_show_chain_commands)

    parser_mine = subparsers.add_parser('mine', help='mine for a new block.')
    parser_mine.set_defaults(func=mine_block)

    parser_create_genesis = subparsers.add_parser('create_genesis', help='create genesis block.')
    parser_create_genesis.set_defaults(func=create_genesis)

    parser_sync = subparsers.add_parser('sync', help='sync data from other nodes.')
    parser_sync.set_defaults(func=sync_nodes)

    if len(sys.argv) == 1:
        print parser.format_help()
        return

    args = parser.parse_args()
    args.func()

if __name__ == '__main__':
    main()