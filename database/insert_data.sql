INSERT INTO skill_tests (name, description) VALUES
("Terminal", "Simulate on-the-spot CLI tasks that validate navigation and command mastery."),
("Python Virtual Environments and Maven", "Tackle mixed-environment workflows, from venv activation to Maven lifecycle knowledge."),
("Deploy on AWS", "Walk through high-level deployment considerations and the services needed to ship safely.");

INSERT INTO questions (skill_test_id, prompt, answer, category) VALUES
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command lists files in a directory, including hidden ones?', 'ls -a', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command moves a file named notes.txt to /home/user/docs/ and renames it to archive.txt in the same step?', 'mv notes.txt /home/user/docs/archive.txt', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command displays the directory you are currently in?', 'pwd', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command creates a new directory named "new_folder" in the current directory?', 'mkdir new_folder', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command changes the current working directory to /home/user/projects/', 'cd /home/user/projects/', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command opens the man page for chmod?', 'man chmod', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What key quits a man page?', 'q', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command displays the contents of a file named README.md?', 'cat README.md', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command creates a new file named "todo.txt" in the current directory?', 'touch todo.txt', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command deletes a file named "junk.txt" in the current directory?', 'rm junk.txt', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'You are in /var/log/nginx/. What command moves you up two directories to /var/?', 'cd ../../var', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command opens a file named notes.txt in the terminal text editor?', 'nano notes.txt', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command searches for "hello" in every .txt file in the current directory?', 'grep "hello" *.txt', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command lists all files, filters to only .txt files, and prints them one per line?', 'ls | grep ".txt"', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command opens book.txt in less so you can scroll up and down?', 'less book.txt', 'Terminal'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'What command counts the number of lines in data.csv?', 'wc -l data.csv', 'Terminal');

INSERT INTO study_guides (skill_test_id, content) VALUES
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'Manipulate files and directories in the terminal using various commands.'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'Edit files within the terminal using commands such as nano.'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'Navigate the file system using commands such as pwd, cd, etc.'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'Pipe commands together using the | symbol.'),
((SELECT id FROM skill_tests WHERE name = "Terminal"), 'Use the man command to view documentation for commands.'),
((SELECT id FROM skill_tests WHERE name = "Python Virtual Environments and Maven"), 'Create a Python virtual environment and install packages using the requirements.txt file.'),
((SELECT id FROM skill_tests WHERE name = "Python Virtual Environments and Maven"), 'Answer questions about third-party libraries and other concepts related to virtual environments.'),
((SELECT id FROM skill_tests WHERE name = "Python Virtual Environments and Maven"), 'Understand the Maven lifecycle and how to use it to build and deploy applications.'),
((SELECT id FROM skill_tests WHERE name = "Python Virtual Environments and Maven"), 'Answer questions about dependency management, the build process, and other concepts related to Maven.'),
((SELECT id FROM skill_tests WHERE name = "Python Virtual Environments and Maven"), 'Explain how activate and deactivate scripts modify the $PATH.'),
((SELECT id FROM skill_tests WHERE name = "Python Virtual Environments and Maven"), 'Explain the contents of the pom.xml file.'),
((SELECT id FROM skill_tests WHERE name = "Deploy on AWS"), 'Copy a systemd .service file into the appropriate location.'),
((SELECT id FROM skill_tests WHERE name = "Deploy on AWS"), 'Know how to launch and SSH into an AWS EC2 instance.'),
((SELECT id FROM skill_tests WHERE name = "Deploy on AWS"), 'Answer questions about EC2, SSH, yum, firewalls, systemd, and curl.'),
((SELECT id FROM skill_tests WHERE name = "Deploy on AWS"), 'Launch a web server using systemd.');
((SELECT id FROM skill_tests WHERE name = "Deploy on AWS"), 'Understand the purpose of gunicorn and flask.');

