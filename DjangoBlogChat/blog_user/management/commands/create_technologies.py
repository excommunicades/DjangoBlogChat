# myapp/management/commands/create_technologies.py
from django.core.management.base import BaseCommand
from blog_user.models import Technologies

class Command(BaseCommand):

    help = 'Create 50 technologies in the database'

    def handle(self, *args, **kwargs):
        technologies = [
            ("Python", "A high-level, interpreted programming language."),
            ("JavaScript", "A high-level, just-in-time compiled programming language for web development."),
            ("CSS", "A stylesheet language used for describing the presentation of a document written in HTML or XML."),
            ("HTML", "The standard markup language for creating web pages and web applications."),
            ("Ruby", "A dynamic, open source programming language with a focus on simplicity and productivity."),
            ("Java", "A high-level, class-based, object-oriented programming language."),
            ("C#", "A modern, object-oriented programming language developed by Microsoft."),
            ("C++", "A general-purpose programming language with low-level memory manipulation capabilities."),
            ("PHP", "A popular general-purpose scripting language especially suited for web development."),
            ("Swift", "A general-purpose, compiled programming language developed by Apple for iOS and macOS applications."),
            ("Go", "A statically typed, compiled programming language designed by Google."),
            ("Rust", "A systems programming language focused on safety, speed, and concurrency."),
            ("TypeScript", "A superset of JavaScript that adds static typing."),
            ("SQL", "A domain-specific language used in programming and managing relational databases."),
            ("NoSQL", "A type of database that provides a mechanism for data storage and retrieval that is modeled differently from the relational model."),
            ("Django", "A high-level Python web framework that encourages rapid development and clean, pragmatic design."),
            ("Flask", "A micro web framework written in Python."),
            ("React", "A JavaScript library for building user interfaces."),
            ("Vue.js", "A progressive JavaScript framework used to build web interfaces and single-page applications."),
            ("Angular", "A TypeScript-based open-source framework for building web applications."),
            ("Node.js", "A runtime environment that allows you to run JavaScript code outside of a web browser."),
            ("Kotlin", "A statically typed programming language that runs on the JVM, Android, JavaScript, and native platforms."),
            ("Ruby on Rails", "A server-side web application framework written in Ruby."),
            ("Laravel", "A PHP framework for web application development."),
            ("Spring", "A comprehensive programming and configuration model for Java-based enterprise applications."),
            (".NET", "A framework developed by Microsoft that allows developers to create applications for Windows, web, and mobile platforms."),
            ("Unity", "A cross-platform game engine used to develop 2D and 3D games."),
            ("Unreal Engine", "A real-time 3D creation tool used for developing games, simulations, and other visual media."),
            ("TensorFlow", "An open-source machine learning framework developed by Google."),
            ("PyTorch", "An open-source machine learning framework used for applications like computer vision and natural language processing."),
            ("OpenCV", "An open-source computer vision and machine learning software library."),
            ("Flutter", "An open-source UI software development kit used to create natively compiled applications for mobile, web, and desktop."),
            ("Docker", "A platform used to develop, ship, and run applications inside lightweight containers."),
            ("Kubernetes", "An open-source system for automating the deployment, scaling, and management of containerized applications."),
            ("AWS", "Amazon Web Services is a comprehensive, evolving cloud computing platform provided by Amazon."),
            ("Azure", "A cloud computing platform and service created by Microsoft."),
            ("Google Cloud", "A suite of cloud computing services provided by Google."),
            ("Git", "A distributed version control system used to track changes in source code during software development."),
            ("GitHub", "A platform for version control and collaboration, enabling developers to work together on projects."),
            ("GitLab", "A web-based DevOps lifecycle tool that provides a Git repository manager providing wiki, issue tracking, and CI/CD pipeline features."),
            ("Jenkins", "An open-source automation server used to build, test, and deploy software."),
            ("Ansible", "An open-source automation tool used to automate software provisioning, configuration management, and application deployment."),
            ("Terraform", "An open-source infrastructure as code software tool used to manage and provision infrastructure."),
            ("Chef", "An automation platform that manages infrastructure as code."),
            ("Puppet", "An open-source software configuration management tool."),
            ("Vagrant", "An open-source software product for building and maintaining virtualized development environments."),
            ("Hadoop", "An open-source framework used for distributed storage and processing of large data sets."),
            ("Spark", "An open-source, distributed computing system that provides an interface for programming entire clusters with implicit data parallelism and fault tolerance."),
            ("Redis", "An open-source, in-memory data structure store used as a database, cache, and message broker."),
            ("MongoDB", "A document-oriented NoSQL database program."),
            ("MySQL", "An open-source relational database management system."),
            ("PostgreSQL", "An open-source, object-relational database system."),
        ]

        for name, description in technologies:
            Technologies.objects.create(name=name, description=description)

        self.stdout.write(self.style.SUCCESS('Successfully created 50 technologies'))
