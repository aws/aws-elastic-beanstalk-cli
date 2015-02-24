#!/usr/bin/env python
# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""The all in one, windows building script.

This basically does two things:

    * Creates a self contained install of the CLI via py2exe.
    * Creates an MSI via WiX.

"""
import codecs
import sys
import os
import shutil
import argparse
import zipfile
from contextlib import contextmanager
from subprocess import Popen, PIPE, call, check_call
# opcode is used to figure out where the non-virtualenv
# python is located.
import opcode


PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
GLOBAL_SITE_PACKAGES = os.path.join(os.path.dirname(opcode.__file__), 'site-packages')


PRODUCT_WIX = """\
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" Name="AWS Elastic Beanstalk Command Line Interface"
            Language="1033" Version="{cli_version}" Manufacturer="Amazon Web Services Developer Relations"
            UpgradeCode="08f203e2-387b-40b5-af57-84d9671917c4">
        <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" Platform="{architecture}" />

        <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed. Exiting installation." />
        <!--<MediaTemplate />-->

        <Condition Message="A newer version of [ProductName] is already installed. Exiting installation.">
            <![CDATA[Installed OR NOT NEWER_VERSION_FOUND]]>
        </Condition>

        <Media Id="1" Cabinet="media1.cab" EmbedCab="yes" />

        <Feature Id="AWSEBCLI" Title="AWS Elastic Beanstalk Command Line Interface" Level="1"
                Display="expand" AllowAdvertise="no" ConfigurableDirectory="{id_prefix}"
                Description="The AWS Elastic Beanstalk Command Line Interface is a tool to
                            manage your AWS Elastic Beanstalk environments.">
            <ComponentGroupRef Id="{id_prefix}_Files" />
            <Component Id="SetCLIPathEnvironment" Directory="{id_prefix}" Guid="e97b7821-3f0f-453f-8c39-bbced31e72fa">
                <CreateFolder/>
                <Environment Id="SET_ENV" Action="set" Name="PATH" Part="last" Permanent="no" System="yes" Value="[{id_prefix}]" />
            </Component>
        </Feature>
        <Icon Id="awsicon" SourceFile="resources\\amazonaws.ico" />
        <Property Id="ARPPRODUCTICON" Value="awsicon" />
        <WixVariable Id="WixUIBannerBmp" Value="resources\\logo_aws.jpg" />
        <WixVariable Id="WixUIDialogBmp" Value="resources\\dialog.jpg" />
        <WixVariable Id="WixUILicenseRtf" Value="LICENSE.rtf" />
        <UIRef Id="WixUI_FeatureTree" />
    </Product>

    <Fragment>
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="{program_files}">
                <Directory Id="AmazonProgramsFolderRoot" Name="Amazon">
                    <Directory Id="{id_prefix}" Name="AWSEBCLI">
                    </Directory>
                </Directory>
            </Directory>
        </Directory>
    </Fragment>

</Wix>
"""
LICENSE_RTF = """\
{\\rtf1\\ansi\\deff0\\nouicompat{\\fonttbl{\\f0\\fnil\\fcharset0 Courier New;}}
{\\*\\generator Riched20 6.2.9200}\\viewkind4\\uc1
\\pardb\\f0\\fs24\\lang1033 AWS Elastic Beanstalk Command Line Interface\\par

\\pard\\b0\\fs22\\par
Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.\\par
\\par
Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at\\par
\\par
    http://aws.amazon.com/apache2.0/\par
\par
or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.\par
\par
}
 """

NOTICE_RTF = codecs.decode(codecs.decode(b"""\
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
Oe39hPSfpSs8/h86UzNF
""", "base64"), "zlib")



AMAZONAWS_ICO = codecs.decode(codecs.decode(b"""\
eNrtkzEKwjAYhV9QUNChILi2m465gR7BYzj2COku9AgeQfAC9QY5Qo8Q3LrFF5pCCFEK2s2EL5CX
//uHkACCM8vAtcB5DmwB7AkjJn0+jM2qZ6qxuxlJatIS5bmS00jHBgz+sDepXpHzyQ8xX/r270/q
a3L06JG+qytJsb53jtJTuMyf6YQfO5rYCB33Ct8gc0VMwotxNerdX+CZ9L2awGl8Jn/9Xy1voTsA
jwWgRIqLUGKJqgLqp7VdztoZnbx3X0Tt4rE=
""", "base64"), "zlib")



DIALOG_JPG = codecs.decode(codecs.decode(b"""\
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
y/5l/7J/2b/s/2uTFs/8D83WBOE=
""", "base64"), "zlib")


LOGO_AWS_JPG = codecs.decode(codecs.decode(b"""\
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
""", "base64"), "zlib")


def run(cmd, env=None):
    sys.stdout.write("Running cmd: %s\n" % cmd)
    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, env=process_env)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()
    if p.returncode != 0:
        raise Exception("Bad rc (%d): %s" % (p.returncode, stdout + stderr))
    return stdout + stderr


@contextmanager
def cd(directory):
    original = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(original)


PLATFORM = run('%s -c "import platform; print(platform.architecture()[0])"'
               % sys.executable).strip().lower()


def _write_resources():
    resource_dir = os.path.join('output', 'resources')
    if not os.path.isdir(resource_dir):
        os.makedirs(resource_dir)
    with open(os.path.join('output', 'LICENSE.rtf'), 'w') as f:
        f.write(LICENSE_RTF)
    with open(os.path.join('output', 'resources', 'amazonaws.ico'), 'wb') as f:
        f.write(AMAZONAWS_ICO)
    with open(os.path.join('output', 'resources', 'dialog.jpg'), 'wb') as f:
        f.write(DIALOG_JPG)
    with open(os.path.join('output', 'resources', 'logo_aws.jpg'), 'wb') as f:
        f.write(LOGO_AWS_JPG)


def check_preconditions():
    # This script must be run from where the setup.py is run.
    if not os.path.isfile('setup.py'):
        sys.stderr.write("This script must be run from the same directory "
                         "as the setup.py file.\n")
        sys.exit(1)
    try:
        assert call('candle') == 0
    except (WindowsError, AssertionError):
        sys.stderr.write("Must have candle.exe on your path\n")
        sys.exit(1)
    try:
        assert call('light') == 0
    except (WindowsError, AssertionError):
        sys.stderr.write("Must have light.exe on your path\n")
        sys.exit(1)
    # Must have py2exe installed.
    try:
        # The py2exe msi puts the package in the global site-packages dir
        # and we generally run this script in a virtualenv, so we need
        # to add this to the PYTHONPATH whenever we do anything py2exe
        # related.
        run('%s -c "import py2exe"' % sys.executable,
            env={'PYTHONPATH': GLOBAL_SITE_PACKAGES})
    except Exception:
        sys.stderr.write("Must have py2exe python package installed\n")
        sys.exit(1)
    # This is not strictly an error, *but* we should be using the latest
    # release of python2.7 so we're going to enforce that here.
    if sys.version_info[:3] != (3, 4, 2):
        sys.stderr.write("Must have python 3.4.2 installed, not: %s\n" % sys.version)
        sys.exit(1)


def generate_exe():
    create_working_dir()
    download_dependencies()
    run_setup_py2exe()
    # copy_extra_data_files(args)
    # HACK_DISTUTILS()
    move_output_dir()


def move_output_dir():
    final_dir = os.path.join('output', 'awsebcli')
    if os.path.isdir(final_dir):
        shutil.rmtree(final_dir)
    shutil.move('dist', final_dir)


def copy_extra_data_files(args):
    # Data directories (things like our .json models).
    python = sys.executable
    boto_data = run("""%s -c "import ebclibotocore,os; print(os.path.join(os.path.dirname(botocore.__file__), 'data'))" """ % python).strip()
    cli_data = run("""%s -c "import awscli,os; print(os.path.join(os.path.dirname(awscli.__file__), 'data'))" """ % python).strip()
    print(boto_data)
    print(cli_data)
    shutil.copytree(boto_data, os.path.join('dist', 'botocore', 'data'))
    shutil.copytree(cli_data, os.path.join('dist', 'awscli', 'data'))

    # We need the cacert.pem from the requests library so we have
    # to copy that in dist.
    ca_cert = run("""%s -c "import botocore.vendored.requests,os; print(os.path.join(os.path.dirname(botocore.vendored.requests.__file__), 'cacert.pem'))" """ % python).strip()
    shutil.copy(ca_cert, os.path.join('dist', 'botocore', 'vendored', 'requests', 'cacert.pem'))

    # And finally the example .rst files.
    cli_data = run("""%s -c "import awscli,os; print(os.path.join(os.path.dirname(awscli.__file__), 'examples'))" """ % python).strip()
    shutil.copytree(cli_data, os.path.join('dist', 'awscli', 'examples'))
    # Copy over the NOTICE.rtf file.
    with open(os.path.join('dist', 'NOTICE.rtf'), 'w') as f:
        f.write(NOTICE_RTF)


def HACK_DISTUTILS():
    # Yes, this is in all caps on purpose.
    # Yes this is a *SUPER* hack.
    # So the problem is the virtualenv patched version of
    # distutils if it looks like it's the system version of
    # distutils.  This is actually fine in our case because
    # we *are* the only distutils in our self contained directory.
    # So here's the hack. First, find out where distutils is.
    python = sys.executable
    filename = run('%s -c "import distutils;print(distutils.__file__)"' % python).strip().rstrip('c')
    with open(filename) as f:
        contents = f.read()
    # Now we look for the place where the hacked distutils is warning us.
    start = contents.find('warnings.warn(')
    assert start != -1
    # Then we find where the end of the warnings call is.
    end = None
    for index in xrange(start + len('warnings.warn('), len(contents)):
        if contents[index] == ')':
            end = index
            break
    else:
        raise Exception("Couldn't find end paren")
    # Then we replace the warnings.warn(...) call with a 'pass'
    # statement.  Yes this is really happening.
    new_contents = contents[:start] + 'pass' + contents[end+1:]
    # Then we write out the new file.
    with open('__init__.py', 'w') as f:
        f.write(new_contents)
    # Then we compile it to a pyc file.
    import py_compile
    py_compile.compile('__init__.py')
    # Then we move the compiled pyc file over to the distutils dir.
    shutil.copy('__init__.pyc', os.path.join('dist', 'distutils', '__init__.pyc'))
    # Then remove any trace of the terrible hack we've done.
    os.remove('__init__.pyc')
    os.remove('__init__.py')


def run_setup_py2exe():
    try:
        run('%s setup.py py2exe' % sys.executable,
            env={'PYTHONPATH': GLOBAL_SITE_PACKAGES})
    except:
        pass


def create_working_dir():
    if os.path.isdir('dist'):
        shutil.rmtree('dist')
    working_dir = os.path.join(PARENT_DIR, 'output')
    if not os.path.isdir(working_dir):
        os.makedirs(working_dir)


def download_dependencies():
    run('python setup.py install')


def generate_msi():
    version = run("""%s -c "import ebcli; print(ebcli.__version__);" """ % sys.executable).strip()
    if PLATFORM == '64bit':
        id_prefix = 'AWSEBCLI64'
        architecture = 'x64'
        program_files = 'ProgramFiles64Folder'
    elif PLATFORM == '32bit':
        id_prefix = 'AWSEBCLI32'
        architecture = 'x86'
        program_files = 'ProgramFilesFolder'
    else:
        raise Exception('Error. Must run from windows x64 or x86. Platform = ' + str(PLATFORM))
    context = {
        'cli_version': version,
        'id_prefix': id_prefix,
        'architecture': architecture,
        'program_files': program_files,
        }
    _write_resources()
    _generate_wix_files(output_dir='output', context=context)
    _build_msi(id_prefix + '.msi', output_dir='output',
               architecture=architecture)


def _build_msi(msi_name, output_dir, architecture):
    with cd(output_dir):
        run('candle.exe -v -arch %s -ext WixUIExtension Product.wxs '
            'Contents.wxs' % architecture).split()
        run('light.exe -sval -b awsebcli -v -ext WixUIExtension -out %s '
            'Product.wixobj Contents.wixobj' % msi_name).split()


def _generate_wix_files(output_dir, context):
    _generate_product_wix(output_dir, context)
    _generate_contents_wix(output_dir, context)


def _generate_product_wix(output_dir, context):
    with open(os.path.join(output_dir, 'Product.wxs'), 'w') as f:
        f.write(PRODUCT_WIX.format(**context))


def _generate_contents_wix(output_dir, context):
    with open(os.path.join(output_dir, 'Contents.wxs'), 'w') as f:
        with cd(os.path.join(output_dir, 'awsebcli')):
            _create_contents_wix(context, f)


def _create_contents_wix(context, out_stream):
    id_prefix = context['id_prefix']
    out_stream.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    out_stream.write('<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">\n')
    out_stream.write('<Fragment>\n')
    # First write out all the directories.
    for root, dirnames, filenames in os.walk('.'):
        if root == '.':
            current_id_prefix = id_prefix
        else:
            current_id_prefix = id_prefix + '_' + os.path.normpath(
                root).upper().replace(os.sep, '_')
        current_id_prefix = current_id_prefix.replace('-', '_')
        out_stream.write('<DirectoryRef Id="%s">\n' % current_id_prefix)
        for dirname in dirnames:
            dirname = dirname.replace('-', '_')
            out_stream.write('\t<Directory Id="%s_%s" Name="%s" />\n' % (
                current_id_prefix, dirname.upper().replace('-', '_'),
                dirname))
        out_stream.write('</DirectoryRef>\n')
    # And now write out all the files.
    out_stream.write('<ComponentGroup Id="%s_Files">\n' % id_prefix)
    for root, dirnames, filenames in os.walk('.'):
        if root == '.':
            current_id_prefix = id_prefix
        else:
            current_id_prefix = id_prefix + '_' + os.path.normpath(
                root).upper().replace(os.sep, '_')
        current_id_prefix = current_id_prefix.replace('-', '_')
        if filenames:
            for filename in filenames:
                file_id = '%s_%s' % (current_id_prefix,
                                     filename.upper().replace('-', '_'))
                source = os.path.normpath(os.path.join(root, filename))
                out_stream.write('<Component Directory="%s">\n' % current_id_prefix)
                out_stream.write('\t<File Source="%s" Id="%s" />\n' % (source,
                                                                       file_id))
                out_stream.write('</Component>\n')
    out_stream.write('</ComponentGroup>\n')
    out_stream.write('</Fragment>\n')
    out_stream.write('</Wix>\n')


def backup_dist_dir():
    if os.path.isdir('dist'):
        shutil.copytree('dist', 'dist.backup')


def restore_dist_dir():
    if os.path.isdir('dist.backup'):
        if os.path.isdir('dist'):
            shutil.rmtree('dist')
        shutil.move('dist.backup', 'dist')


def main():
    check_preconditions()
    backup_dist_dir()
    try:
        generate_exe()
        generate_msi()
        # zip_exe_dir(args)
    finally:
        restore_dist_dir()

if __name__ == '__main__':
    main()