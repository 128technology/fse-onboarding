FROM centos:centos7

# Set up repos
RUN yum install -y epel-release

RUN curl –sL https://rpm.nodesource.com/setup_13.x | bash -

# Install required packages
RUN yum install -y \
        python3 \
        python3-pip \
        screen \
        openssh \
        nodejs \
        openssh-clients \
        rsync

ENV container=docker \
        DOCKER_NAME="provisioner"

# Set Prompt
COPY docker_prompt.sh /etc/profile.d

# Set Locale
COPY docker_locale.sh /etc/profile.d

# Install pip packages
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

# Install base provisioner library
COPY python/provisioner /tmp/provisioner
RUN pip3 install /tmp/provisioner

# Install FSE provisioner library
COPY python/fse /tmp/fse
RUN pip3 install /tmp/fse

# Install FSE entry points
COPY fse/scripts /usr/share/128T-provisioner/scripts

# Create symlinks from entry points to /usr/local/bin
RUN ln -s /usr/share/128T-provisioner/scripts/* /usr/local/bin/

# Install FSE config templates
# COPY fse/config_templates /usr/share/128T-provisioner/config_templates

# Install fse-cmd-runner webserver packages
COPY fse/web /var/www/fse-cmd-runner
WORKDIR /var/www/fse-cmd-runner
RUN npm install

# Prepare ssh key directory for NETCONF operations
RUN mkdir -p /home/admin/.ssh

EXPOSE 3006

# Copy initialize script
COPY initialize.sh /

# Start the web app
WORKDIR /var/www/fse-cmd-runner
CMD bash -c "/initialize.sh && npm run start"
