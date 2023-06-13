<h1 align="center">LDAP Reset Password - Focused Active Directory</h1>

<p align="center">
    This project can be used to reset user password in LDAP server, we use the Python and LDAP protocol to manager users in Directory Server.
</p>

## Configurations

### Active Directory

To deploy this project you need an Active Directory (AD) server to connect LDAP Reset Password, so, your first step is configure your AD server.

AD has many secutiry protocols to update user data, for example, we need use secugiry port from ldap connection (port 636), the unsecurity port (379) can be used only to read data.

We need to export AD certificate and import in your application server, below i gonna show how you can do this.

#### Export AD certificate

1. First step, go to your Active Directory server
2. Open PowerShell as Administrator
3. Run certmgr.msc to open certificate list
4. To Navigate for certificate list, click in Trusted Toot Certification Authorities > Certificates
5. Select the certificate with same name from your AD server and click with right buttom from mouse
6. Click in All Tasks > Export
7. Select the Base-64 encoded X.509 (.CER) and click next
8. Select a diretory to save and click next
9. Click Finish

### Linux Server

Now you have a Active Directory certicate to use in your Linux server, in my case i am using a Ubuntu 22.04

I use the command below to test Activie Directpry connection.

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


Obs: For your first test you can see the unsecure port ldap connection working but secure port with error, for resolve this issue we need import Active Directory certificate in our linux server, so we gonna make this now.

#### Add Active Directory in our linux server

For example have the LDAP-Test.cer created in the Export AD Certificate step, i put this file in my /Documents/certs folder.

The steps below can used to add cert file in certificates linux folder.

