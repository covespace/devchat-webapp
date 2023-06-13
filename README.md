# webapp
Web application for DevChat and covespace.

## Deployment

Please note that the values provided below are for example purposes only.

### Environment Variables for Frontend

To set the environment variables for the frontend, either edit the `frontend/.env.local` file or set the following two environment variables.

```
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_HCAPTCHA_SITEKEY=your_site_key_here
```

### Environment Variables for Backend

For the backend, set the following five environment variables. You can edit the `tests/.env` file to run pytest.

```
JWT_SECRET_KEY=50a3b8e5886c367d57e3cd3c6f61112403170d7f9238bc87aa2f8d186b5f1a8d
DATABASE_URL=postgresql://merico@localhost/devchat_test
SENDGRID_TEMPLATE_ID=d-502575d72d61a200b23a3aa8e01822bc
SENDGRID_API_KEY=your_sendgrid_api_key_here
HCAPTCHA_SECRET_KEY=your_hcaptcha_secret_key_here
```
