# EduAccess AI - AWS Deployment Guide

This guide provides step-by-step instructions for deploying EduAccess AI to a production AWS EC2 environment using Ubuntu, Gunicorn, and Nginx.

## 1. AWS IAM Recommendations
For the EC2 instance, ensure the following Identity and Access Management (IAM) best practices are followed:
- **IAM Role:** Create an IAM Role specifically for this EC2 instance (e.g., `EduAccess-EC2-Role`). Do not embed long-term AWS access keys on the server.
- **SSM Access:** Attach the `AmazonSSMManagedInstanceCore` policy to the IAM role so you can access the instance securely via AWS Systems Manager (Session Manager) without opening port 22 to the internet.
- **Least Privilege:** Ensure the role has only the exact permissions needed.

## 2. AWS Security Groups (Firewall)
Configure the Security Group attached to your EC2 instance with the following inbound rules:

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 80 | TCP | 0.0.0.0/0 | Allow HTTP traffic (Nginx) |
| 443 | TCP | 0.0.0.0/0 | Allow HTTPS traffic (SSL/TLS) |
| 22 | TCP | Your IP | (Optional) SSH Access. Better to use Session Manager. |

*Note: Port 5000 (Gunicorn) should **not** be open to the internet. Nginx will handle external requests on port 80/443 and securely proxy them to Gunicorn locally.*

## 3. EC2 Instance Setup (Ubuntu 22.04 LTS)

Launch a `t3.micro` or `t3.small` EC2 instance using the **Ubuntu Server 22.04 LTS** AMI. Attach the IAM role and Security Group defined above. 

Once connected to the instance, update packages and install dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx git -y
```

## 4. Application Setup

Clone the repository and set up the Python virtual environment:

```bash
git clone https://github.com/your-repo/EduAccess-AI.git
cd EduAccess-AI

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

Set up your environment variables:
```bash
cp ../.env.example ../.env
nano ../.env
```
*Change `FLASK_ENV=production` and add your `GEMINI_API_KEY`.*

## 5. Running with Gunicorn via systemd

Create a `systemd` service file so Gunicorn starts automatically on boot and restarts if it crashes.

```bash
sudo nano /etc/systemd/system/eduaccess.service
```

Add the following configuration (replace `/home/ubuntu` with your path):

```ini
[Unit]
Description=Gunicorn instance to serve EduAccess AI
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/EduAccess-AI/backend
Environment="PATH=/home/ubuntu/EduAccess-AI/venv/bin"
ExecStart=/home/ubuntu/EduAccess-AI/venv/bin/gunicorn -c gunicorn_config.py run:app

[Install]
WantedBy=multi-user.target
```

Start and enable the service:
```bash
sudo systemctl start eduaccess
sudo systemctl enable eduaccess
```

## 6. Configure Nginx (Reverse Proxy)

Nginx will accept external traffic and proxy it to Gunicorn.

```bash
sudo nano /etc/nginx/sites-available/eduaccess
```

Add the configuration:

```nginx
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/eduaccess /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Next Steps (SSL/TLS)
For a production application, it is highly recommended to secure the domain with HTTPS using **Certbot**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

The application is now successfully deployed! 🚀
