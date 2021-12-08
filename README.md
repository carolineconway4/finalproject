Video Link: https://youtu.be/5QwFSMmsdmw 

The websiste Knit By CC enables customers to commission custom-made knit pieces, while allowing the knitters to divide the commissions amongst themselves and keep track of their projects. Knit By CC is a flask-based website - in order to run the site, the files should be uploaded to the IDE and the command "flask run" should be executed in the terminal. To enable the website to send emails to customers, I have utilized the flask_mail dictionary. I set my email password using the os.environ functionality. . 

When viewing the website as a customer, you will need to register and log-in with an email and password in order to add items to your cart (if you attempt to add items when not logged in, an error message should appear). Note, that you must be logged in as a customer (NOT a knitter) to add items to your cart. You can add as many items to your cart as you would like, and you can view the items under the cart tab. When viewing the cart tab, you can delete items from your cart or you can check out. Once you check out, you should receive an email notifying you that your order has been received. As a customer, you can access our home page, about us page, store page, individual item pages, contact us, and our Instagram. 

To view the website as a knitter, navigate to the footer of the webpage and select the link that says Knitter Log In. The Knitter Log In page is password-protected to prevent customers from registering as knitters; the password to this page is "KnitByCC123!". Once you have entered the correct password, it will redirect you to the knitter log in and registration pages. You are free to register as a knitter and log in with your own account if you would like; you could also use my account to access the knitter homepage. Once you have logged in as a knitter, it will direct you to the knitter homepage. At the top of the page you will see a table called New Projects. This table contains all of the information on projects that have been commissioned that have not yet been claimed by a knitter. This table will be the same for all knitters. If you would like to take on a project, click the "Accept Project" button. When you select this button, the customer will be notified that their project has been accepted by a knitter, and the project will move down to the second table on the page. The second table is labeled "My Projects" and it contains all of the projects that the specific knitter has claimed. If the knitter selects the "Complete Project" button, the project will be moved to the sql table "completed_projects" and the customer will receive an email notifying them that their project has been completed. 

Please note that all of the projects currently in the database are not real - so please feel free to submit projects, accept projects, and mark projects as complete!

Quick summary: 
1) upload all files to IDE
2) execute "cd final" in terminal
4) execute "flask run"
5) follow link to explore the website!

