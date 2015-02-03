#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys

from flask import Flask
from flask_frozen import Freezer

import search
from source import app

APP_NAME = 'pelletron'
APP_VERSION = 0.1
PYTHON_VERSION = sys.version_info[0]
RSYNC_ARGS = ''

def load_secret_key(app, filename='secret-key'):
    path = os.path.join(os.curdir, filename)
    try:
        app.config['SECRET_KEY'] = open(path, 'rb').read()
    except IOError:
        print("[ERROR] Failed to load SECRET KEY (path: {})".format(path))
        print("        Create the file by executing the following:")
        print("")
        if not os.path.isdir(os.path.dirname(path)):
            print("            mkdir -p '{}'".format(escape_path(os.path.dirname(path))))
        print("            head -c 32 /dev/urandom > '{}'".format(escape_path(path)))
        print("            chmod go-r '{}'".format(escape_path(path)))
        print("")
        print("        Then re-run the command you just typed:")
        print("")
        print("            {}".format(' '.join(sys.argv)))
        sys.exit(1)

def build(args):
    app.config['PELLETRON_ACTION'] = 'build'
    if not args.quiet:
        print("[BUILD] Generating static site.")
    freezer = Freezer(app)
    freezer.freeze()
    if app.config['SEARCH_ENABLED']:
        build_path = os.path.normpath(os.path.join(app.root_path, app.config['FREEZER_DESTINATION']))
        search.build_search_index(build_path)
    return True

def clean(args):
    app.config['PELLETRON_ACTION'] = 'clean'
    if not args.quiet:
        print("[CLEAN] Deleting generated content.")
    errors = False
    for root, dirs, files in os.walk(os.path.join('source', app.config['FREEZER_DESTINATION']), topdown=False):
        for name in files:
            path = os.path.normpath(os.path.join(root, name))
            try:
                os.remove(path)
                if args.verbose:
                    print("- Delete file: {path}".format(path=path))
            except OSError, err:
                print("[ERROR] Couldn't delete file: {path}. {error}".format(path=path, error=err))
                errors = True
        for name in dirs:
            path = os.path.normpath(os.path.join(root, name))
            try:
                os.rmdir(path)
                if args.verbose:
                    print("- Remove dir: {path}".format(path=path))
            except OSError, err:
                print("[ERROR] Couldn't remove dir: {path}. {error}".format(path=path, error=err))
                errors = True
    return not errors

def deploy(args):
    app.config['PELLETRON_ACTION'] = 'deploy'
    if not args.quiet:
        print("[DEPLOY] Deploying to '{}'.".format(args.host))
    try:
        new_deploy = False
        if not test_ssh(args.host, args.user):
            print("[WARN] To increase security and avoid having to enter the SSH password, set up key-based authentication for '{}@{}': https://www.google.com/search?q=ssh+without+password".format(args.user, args.host))
        ret, out = ssh('test -d {}'.format(args.dir), args.host, args.user)
        if ret != 0:
            if args.nomakedir:
                print("[ERROR] Directory '{}' doesn't exist on {}@{}".format(args.dir, args.user, args.host))
                exit(1)
            else:
                ret, out = ssh('mkdir -p {} && test -d {}'.format(args.dir, args.dir), args.host, args.user)
                if ret == 0:
                    if args.verbose:
                        print("[DEPLOY] Created directory '{}' on {}@{}".format(args.dir, args.user, args.host))
                else:
                    print("[ERROR] Target directory '{}' couldn't be created on {}@{}".format(args.dir, args.user, args.host))
                    exit(1)
        sourcepath = os.path.join(os.path.abspath(os.path.join(app.root_path, app.config['FREEZER_DESTINATION'])), '')
        line = """/usr/bin/rsync -a{}z {}-e 'ssh -p {}' {} {} {}@{}:{}""".format('v' if args.verbose else 'q', '--delete ' if args.delete else '', args.port, RSYNC_ARGS, sourcepath, args.user, args.host, args.dir)
        if args.verbose:
            print("[DEPLOY] {}".format(line))
        output = subprocess.check_output(line, shell=True)
    except Exception, err:
        print("[ERROR] Failed to deploy to host '{}' with username '{}'. {}".format(args.host, args.user, err))
        exit(1)
    print("[DEPLOY] Successfully deployed to '{}'.".format(args.host))
    return True

def ssh(command, host, user=None, args=None, verbose=False, exception_on_error=False):
    retcode = 0
    output = None
    line = ['ssh']
    line.extend([userhost(host, user)])
    if args is None:
        args = []
    if type(args) is not list:
        args = list(args)
    line.extend(args)
    line.extend([command])
    if verbose:
        print("[SSH] {} $ {}".format(userhost(host, user), ' '.join(line)))
    try:
        output = subprocess.check_output(line)
    except subprocess.CalledProcessError, err:
        if exception_on_error:
            raise subprocess.CalledProcessError(err)
        retcode = err.returncode
    return retcode, output

def test_ssh(host, user):
    ret, output = ssh('whoami', host=host, user=user, args=['-q', '-o BatchMode=yes'])
    return ret == 0

def userhost(host, user=None):
    if user is None:
        return host
    else:
        return '{}@{}'.format(user, host)

def serve(args):
    app.config['PELLETRON_ACTION'] = 'serve'
    load_secret_key(app)
    if not args.quiet:
        print("[SERVE] Starting development server on {host}:{port}.".format(host=args.host, port=args.port))
    app.run(host=args.host, port=args.port, debug=True)
    return True

def use(args):
    args.framework = args.framework.lower()
    old_framework = app.config['PELLETRON_FRAMEWORK']
    app.config['PELLETRON_ACTION'] = 'switch'
    if old_framework == args.framework:
        print("[INFO] Already using '{}' framework".format(args.framework))
        exit(0)
    if not args.quiet:
        print("[CONFIG] Changing site framework to '{}'".format(args.framework))
    if args.verbose:
        print("[CONFIG] Current framework: '{}'".format(old_framework))
    try:
        import importlib
        importlib.import_module('source.modules.' + args.framework)
    except ImportError, err:
        print("[ERROR] Unable to import framework for '{}'. {}".format(args.framework, err))
    for subdir in ['static', 'templates']:
        # Unlink old framework path
        oldpath = os.path.join('source', subdir, old_framework)
        if args.verbose:
            print("[CONFIG] Unlinking: '{}'".format(escape_path(oldpath)))
        try:
            os.unlink(oldpath)
        except OSError, err:
            print("[ERROR] Failed to unlink: '{}'. {}".format(escape_path(oldpath), err))
        # Link new framework path
        linkpath = os.path.join('source', subdir, args.framework)
        sourcepath = os.path.relpath(os.path.abspath(os.path.join(app.root_path, 'modules', args.framework, subdir)), os.path.dirname(os.path.abspath(linkpath)))
        if args.verbose:
            print("[CONFIG] Linking: '{}' to '{}'".format(escape_path(sourcepath), escape_path(linkpath)))
        try:
            os.symlink(sourcepath, linkpath)
        except OSError, err:
            print("[ERROR] Failed to link '{}' to '{}'. {}".format(escape_path(sourcepath), escape_path(linkpath), err))
    outpath = 'framework.py'
    try:
        with open(outpath, 'w') as f:
            f.write("PELLETRON_FRAMEWORK = '{}'".format(args.framework))
    except IOError, err:
        print("[ERROR] Failed to write framework config file '{}'. {}".format(outpath, err))

def escape_path(s):
    return s.replace("'", "\\'")

def get_args():
    parser = argparse.ArgumentParser(description="A simple static site generator.", add_help=False)
    parser.add_argument('--version', action='version', version='{} {}'.format(APP_NAME, APP_VERSION), help="Get version information")
    parser.add_argument('--help', action='help', help="Get help on command-line options")
    subparsers = parser.add_subparsers()
    # Build
    parser_build = subparsers.add_parser('build', help="Generate site content")
    parser_build.set_defaults(func=build)
    # Clean
    parser_clean = subparsers.add_parser('clean', help="Remove generated site content")
    parser_clean.set_defaults(func=clean)
    # Deploy
    parser_deploy = subparsers.add_parser('deploy', help="Deploy site to configured production server via SSH", add_help=False)
    parser_deploy.set_defaults(func=deploy)
    parser_deploy.add_argument('-h', '--host', dest='host', action='store', default=app.config['DEPLOY_HOST'], help="Remote hostname")
    parser_deploy.add_argument('-p', '--port', dest='port', action='store', default=app.config['DEPLOY_PORT'], type=int, help="Remote port")
    parser_deploy.add_argument('-u', '--user', dest='user', action='store', default=app.config['DEPLOY_USER'], help="Username")
    parser_deploy.add_argument('-d', '--dir', dest='dir', action='store', default=app.config['DEPLOY_DIR'], help="Target directory")
    parser_deploy.add_argument('-m', '--no-make-dir', dest='nomakedir', action='store_true', default=app.config['DEPLOY_NO_MAKE_DIR'], help="Don't create target directory if needed")
    parser_deploy.add_argument('-D', '--delete', dest='delete', action='store_true', default=app.config['DEPLOY_DELETE'], help="Delete files in target directory that don't exist in source")
    parser_deploy.add_argument('--help', action='help', help="Get help on command-line options")
    # Serve
    parser_serve = subparsers.add_parser('serve', help="Serve site using built-in development server", add_help=False)
    parser_serve.set_defaults(func=serve)
    parser_serve.add_argument('-h', '--host', dest='host', action='store', default=app.config['SERVE_HOST'], help="Hostname")
    parser_serve.add_argument('-p', '-P', '--port', dest='port', action='store', default=app.config['SERVE_PORT'], type=int, help="Port")
    parser_serve.add_argument('--help', action='help', help="Get help on command-line options")
    # Use
    parser_use = subparsers.add_parser('use', help="Change site's configuration")
    parser_use.set_defaults(func=use)
    parser_use.add_argument('-f', '--framework', dest='framework', action='store', default=app.config['PELLETRON_FRAMEWORK'], help="Front-end framework")
    # Options
    output_group = parser.add_mutually_exclusive_group(required=False)
    output_group.add_argument('-q', '--quiet', action='store_true', dest='quiet', help="Surpress output messages")
    output_group.add_argument('-v', '--verbose', action='store_true', dest='verbose', help="Output more information about what's going on")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    args.func(args)
