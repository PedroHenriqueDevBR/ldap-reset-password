<h1 align="center">LDAP Reset Password - Focused Active Directory</h1>

<p align="center">
    This project can be used to reset a user's password in an LDAP server. We utilize Python and the LDAP protocol to manage users in the Directory Server.
</p>

## Configurations

### Active Directory

To deploy this project, you will need an Active Directory (AD) server to connect with the LDAP Reset Password functionality. Therefore, your first step is to configure your AD server.

AD employs various security protocols to update user data. For instance, it is essential to use the secure port (port 636) for LDAP connections, as the insecure port (port 389) should only be used for reading data.

We need to export the AD certificate and import it into your application server. Below, I will show you how to accomplish this.

#### Export AD certificate

1. Go to your Active Directory server;
2. Open PowerShell as Administrator;
3. Run **certmgr.msc** to open certificate list;
4. To Navigate for certificate list, click in **Trusted Toot Certification Authorities** > **Certificates**;
5. Select the certificate with same name from your AD server and click with right buttom from mouse;
6. Click in **All Tasks** > **Export**;
7. Select the **Base-64 encoded X.509 (.CER)** and click next;
8. Select a diretory to save and click next;
9. Click Finish.

### Linux Server

Now you have an Active Directory certificate to use in your Linux server. In my case, I am using Ubuntu 22.04.

#### Test LDAP Connection

I am using the command below to test the Active Directory connection.

Please run the LDAP search test on your Linux server. The test is considered successful if it returns a list of users.

```shell
# Without security port
ldapsearch -H ldap://192.168.0.54:389 -D 'CN=Test AD,OU=development,OU=enterprise,DC=adtest,DC=org' -w 9a2@a99c9499 -b "dc=adtest,dc=org" -s sub "(objectClass=user)" givenName

# With security port
ldapsearch -H ldaps://192.168.0.54:636 -D 'CN=Test AD,OU=development,OU=enterprise,DC=adtest,DC=org' -w 9a2@a99c9499 -b "dc=adtest,dc=org" -s sub "(objectClass=user)" givenName

-H -> LDAP Uniform Resource Identifier(s)
-D -> bind DN
-w -> bind password (for simple authentication)
-b -> base dn for search
-s -> one of base, one, sub or children (search scope)
```

Obs: For your first test, you may observe that the LDAP connection on the insecure port is functioning correctly. However, you might encounter an error when attempting to connect through the secure port. To resolve this issue, we need to import the Active Directory certificate into our Linux server. Let's proceed with the certificate importation now.

#### Add Active Directory in our linux server

As an example, let's assume you have the LDAP-Test.cer file created during the Export AD Certificate step. You can place this file in the /Documents/certs folder on your Linux server.

The following steps demonstrate how to add a certificate file to the "certificates" folder on a Linux system:

1. Open a terminal;
2. Navigate to the directory where the certificate file is located (/Documents/certs/ in my documents);
3. Run **sudo cp LDAP-TEST.cer /etc/ssl/certs** to copy certificate to /etc/ssl/certs;
4. Run **sudo update-ca-certificates -f** to update linux certificates.

Now you need to update the LDAP configuration on your server to load the LDAP-TEST.cer certificate. You can follow the steps below to accomplish this:

1. Run **sudo nano /etc/ldap/ldap.conf** to edit the ldap.conf
2. Add the attributes TLS_REQCERT, TLS_CACERT and TLS_CACERTDIR.

```
# /etc/ldap/ldap.conf
-----------------------------------------------------
# TLS certificates (needed for GnuTLS)
TLS_CACERT      /etc/ssl/certs/ca-certificates.crt

TLS_REQCERT never
TLS_CACERT /etc/ssl/certs/LDAP-TEST.cer
TLS_CACERTDIR /etc/ssl/certs
```

## Done server configuration
