from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")


name = "aws_truth_teller"
default_task = "publish"


@init
def set_properties(project):
    project.depends_on('click')
    project.depends_on('boto3')
    project.build_depends_on('datetime')
    project.build_depends_on('unittest2')
