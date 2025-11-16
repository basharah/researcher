# Default Admin User Configuration

## Overview

The API Gateway automatically creates a default admin user on first startup. This user has full administrative privileges and can manage other users, API keys, and system settings.

## Default Credentials

- **Email**: `admin@bashars.eu`
- **Password**: `admin123`
- **Role**: Admin
- **Automatically created**: Yes (on first startup)

## Configuration

You can customize the default admin credentials using environment variables:

### Environment Variables

```bash
DEFAULT_ADMIN_EMAIL=admin@bashars.eu
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_NAME=System Administrator
```

### Setting Custom Credentials

**Option 1: Using .env file** (Development)

```bash
# Add to .env file
DEFAULT_ADMIN_EMAIL=youremail@example.com
DEFAULT_ADMIN_PASSWORD=your-secure-password
DEFAULT_ADMIN_NAME=Your Name
```

**Option 2: Using environment variables** (Production)

```bash
export DEFAULT_ADMIN_EMAIL=youremail@example.com
export DEFAULT_ADMIN_PASSWORD=your-secure-password
export DEFAULT_ADMIN_NAME=Your Name
./start-prod.sh
```

## Manual Admin User Creation

If you need to manually create the admin user in an already-running system:

```bash
./scripts/create-admin-user.sh
```

Or directly:

```bash
docker exec api-gateway-service python init_admin.py
```

## Security Best Practices

⚠️ **IMPORTANT**: Change the default password immediately after first login!

### Steps to Secure Your Admin Account

1. **Login** with default credentials at `http://localhost:3000/login`
2. **Navigate to Profile** (`/profile`)
3. **Change password** to a strong, unique password
4. **Enable two-factor authentication** (if available)
5. **Review API keys** and rotate if necessary

### Password Requirements

- Minimum 8 characters
- Mix of uppercase and lowercase letters
- At least one number
- At least one special character (recommended)

## Admin User Capabilities

The admin user can:

- ✅ Upload and manage all documents
- ✅ Access all user documents
- ✅ Create and manage API keys
- ✅ View all users in the system
- ✅ Enable/disable user accounts
- ✅ Access admin-only endpoints
- ✅ View system analytics and logs

## Troubleshooting

### Admin User Not Created

If the admin user wasn't created automatically:

1. Check API Gateway logs:
   ```bash
   docker logs api-gateway-service | grep -i admin
   ```

2. Run manual creation:
   ```bash
   ./scripts/create-admin-user.sh
   ```

### Admin User Already Exists

If you see "Admin user already exists", the user was created successfully. You can still login with the configured credentials.

### Cannot Login

1. Verify credentials are correct
2. Check if user is disabled:
   ```bash
   docker exec -it researcher-postgres psql -U researcher -d research_papers -c "SELECT email, disabled FROM users WHERE email='admin@bashars.eu';"
   ```
3. Reset password if needed (contact system administrator)

## Related Documentation

- **Authentication Guide**: `docs/AUTHENTICATION_GUIDE.md`
- **API Gateway**: `docs/PHASE4_API_GATEWAY.md`
- **Security Best Practices**: `docs/DEPLOYMENT_COMPLETE.md`

---

**Last Updated**: November 2025
