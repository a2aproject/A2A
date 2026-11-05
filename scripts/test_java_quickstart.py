#!/usr/bin/env python3
"""Build and run the exact Java quickstart snippets (JDK 17+, Maven 3.9+).

Run from any directory with: python scripts/test_java_quickstart.py
Maven downloads dependencies; the server/client interaction is local only.
"""

import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / 'docs/tutorials/java/quickstart.md'
FILES = {
    'server/pom.xml',
    'server/src/main/resources/application.properties',
    'server/src/main/java/example/AgentCardProducer.java',
    'server/src/main/java/example/AgentExecutorProducer.java',
    'client/pom.xml',
    'client/src/main/java/example/HelloWorldClient.java',
}


def run(command, directory):
    subprocess.run(command, cwd=directory, check=True, timeout=1800)


def extract_snippets(directory):
    snippets = re.findall(
        r'Create `([^`]+)`:\n\n```(?:xml|properties|java)\n(.*?)\n```',
        DOCUMENT.read_text(encoding='utf-8'),
        re.DOTALL,
    )
    if len(snippets) != len(FILES) or {path for path, _ in snippets} != FILES:
        raise RuntimeError('Expected exactly six quickstart source files.')
    for name, content in snippets:
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content + '\n', encoding='utf-8')


def wait_for_card(server):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + 60
    while True:
        if server.poll() is not None:
            raise RuntimeError('The server exited during startup.')
        try:
            with opener.open(
                'http://127.0.0.1:9999/.well-known/agent-card.json', timeout=2
            ) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    'Timed out waiting for the Agent Card.'
                ) from error
            time.sleep(0.5)


def verify_card(card):
    if card['name'] != 'Hello World Agent':
        raise RuntimeError('The Agent Card has the wrong name.')
    if card['capabilities']['streaming'] is not False:
        raise RuntimeError(
            'The tutorial must advertise non-streaming behavior.'
        )
    if card['skills'][0]['id'] != 'hello_world':
        raise RuntimeError('The Agent Card has the wrong skill.')


def run_client(maven, directory):
    result = subprocess.run(
        [maven, '-B', '-ntp', '-f', 'client/pom.xml', 'exec:java'],
        cwd=directory,
        check=False,
        capture_output=True,
        text=True,
        timeout=600,
    )
    print(result.stdout)
    print(result.stderr)
    result.check_returncode()
    if 'Discovered: Hello World Agent' not in result.stdout:
        raise RuntimeError(
            'The Java client did not report successful discovery.'
        )
    if 'Response: Hello World' not in result.stdout:
        raise RuntimeError(
            'The Java client did not receive the expected greeting.'
        )


def main():
    java_home = os.environ.get('JAVA_HOME')
    executable = 'java.exe' if os.name == 'nt' else 'java'
    java = (
        str(Path(java_home) / 'bin' / executable)
        if java_home
        else shutil.which(executable)
    )
    maven = shutil.which('mvn.cmd' if os.name == 'nt' else 'mvn')
    if not java or not Path(java).is_file() or not maven:
        raise RuntimeError('Install a JDK and Maven; check JAVA_HOME and PATH.')

    # Do not accidentally test against or stop another process on this port.
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 9999))

    with tempfile.TemporaryDirectory(
        prefix='a2a-java-quickstart-'
    ) as temporary:
        directory = Path(temporary)
        extract_snippets(directory)

        run([maven, '-B', '-ntp', '-f', 'server/pom.xml', 'package'], directory)
        # Compile before starting the server, so dependency downloads do not
        # leave a listening server running unnecessarily.
        run([maven, '-B', '-ntp', '-f', 'client/pom.xml', 'compile'], directory)
        with (directory / 'server.log').open('w+', encoding='utf-8') as log:
            server = subprocess.Popen(
                [java, '-jar', 'server/target/quarkus-app/quarkus-run.jar'],
                cwd=directory,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            try:
                verify_card(wait_for_card(server))
                run_client(maven, directory)
                print('PASS: tutorial snippets compile and exchange a message.')
            except Exception:
                log.flush()
                log.seek(0)
                print(log.read())
                raise
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=10)


if __name__ == '__main__':
    main()
