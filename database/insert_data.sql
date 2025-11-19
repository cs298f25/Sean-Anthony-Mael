INSERT INTO skill_tests (name, description) VALUES
("File Type Identification", "Explore how well you know core DevOps file formats and their use in common pipelines."),
("Terminal", "Simulate on-the-spot CLI tasks that validate navigation and command mastery."),
("Python Virtual Environments and Maven", "Tackle mixed-environment workflows, from venv activation to Maven lifecycle knowledge."),
("Deploy on AWS", "Walk through high-level deployment considerations and the services needed to ship safely.");

INSERT INTO questions (skill_test_id, prompt, answer, category) VALUES
(2, 'What command lists files in a directory, including hidden ones?', 'ls -a', 'Terminal'),
(2, 'What command moves a file named notes.txt to /home/user/docs/ and renames it to archive.txt in the same step?', 'mv notes.txt /home/user/docs/archive.txt', 'Terminal'),
(2, 'What command displays the directory you are currently in?', 'pwd', 'Terminal'),
(2, 'What command creates a new directory named "new_folder" in the current directory?', 'mkdir new_folder', 'Terminal'),
(2, 'What command changes the current working directory to /home/user/projects/', 'cd /home/user/projects/', 'Terminal'),
(2, 'What command opens the man page for chmod?', 'man chmod', 'Terminal'),
(2, 'What key quits a man page?', 'q', 'Terminal'),
(2, 'What command displays the contents of a file named README.md?', 'cat README.md', 'Terminal'),
(2, 'What command creates a new file named "todo.txt" in the current directory?', 'touch todo.txt', 'Terminal'),
(2, 'What command deletes a file named "junk.txt" in the current directory?', 'rm junk.txt', 'Terminal'),
(2, 'You are in /var/log/nginx/. What command moves you up two directories to /var/?', 'cd ../../var', 'Terminal'),
(2, 'What command opens a file named notes.txt in the terminal text editor?', 'nano notes.txt', 'Terminal'),
(2, 'What command searches for "hello" in every .txt file in the current directory?', 'grep "hello" *.txt', 'Terminal'),
(2, 'What command lists all files, filters to only .txt files, and prints them one per line?', 'ls | grep ".txt"', 'Terminal'),
(2, 'What command opens book.txt in less so you can scroll up and down?', 'less book.txt', 'Terminal'),
(2, 'What command counts the number of lines in data.csv?', 'wc -l data.csv', 'Terminal');