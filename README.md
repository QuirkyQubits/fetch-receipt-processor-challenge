# 🧾 fetch-receipt-processor-challenge

This GitHub repo is a submission for the challenge described at:  
https://github.com/fetch-rewards/receipt-processor-challenge

This Django backend project implements a receipt application where users can:

- Upload receipts to the **Process API** to get a unique ID
- Use that ID with the **Points API** to retrieve how many points the receipt is worth

See the detailed API specification:  
https://github.com/fetch-rewards/receipt-processor-challenge/blob/main/api.yml

See valid receipt examples:  
https://github.com/fetch-rewards/receipt-processor-challenge/tree/main/examples

This project includes a Dockerized setup, so you don't need to install Python or Django manually.  
However, **Docker must be installed** on your system.

---

## 🛠️ How to Run (End Users)

### 1. Clone the Repo

```bash
git clone https://github.com/cerulea/fetch-receipt-processor-challenge
cd fetch-receipt-processor-challenge
```

### 2. Build the Docker Image

```bash
docker build -t fetch-receipt-processor-app .
```

### 3. Run the Dockerized Django App

```bash
docker run -d -p 8000:8000 --name my_django_app fetch-receipt-processor-app
```

### 3.1 (Optional) Access Django Admin Console

#### Apply migrations:

```bash
docker exec -it my_django_app python manage.py migrate --noinput
```

#### Create a superuser:

```bash
docker exec -it my_django_app python manage.py createsuperuser
```

Enter:

- Username: `admin`
- Email: `admin@example.com`
- Password: `FetchReceipt`

Now visit [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) to log in and view/edit data.

---

## 🌐 Using the API

### Submit a Receipt

Navigate to:  
[http://127.0.0.1:8000/receipts](http://127.0.0.1:8000/receipts)

Submit a valid JSON string via the form to `/receipts/process`. This returns a receipt ID.

> ⚠️ Directly accessing `/receipts/process` in a browser results in a 400 error.  
> Use the form or send a POST request via cURL/Postman.

### Get Points from Receipt

Navigate to:  
`http://127.0.0.1:8000/receipts/{id}/points`  
Replace `{id}` with the actual receipt ID returned by the process endpoint.

You can open this in a browser to retrieve the points total.

---

## 🛑 Stopping and Removing the Docker Container

```bash
docker ps       # Get <container_id>
docker stop <container_id>
docker rm <container_id>
docker ps -a    # Confirm container is removed
```

---

## 🔍 API Behavior and Edge Case Coverage

All core API logic and edge cases are covered in the test suite. This includes validation, error responses, and formatting edge cases.

See: [tests.py](https://github.com/QuirkyQubits/fetch-receipt-processor-challenge/blob/main/receipts/tests.py)

---

## 🧪 Local Development (Optional, Without Docker)

Activate the virtual environment:

```bash
source ./.virtualenvs/djangodev/Scripts/activate
```

Start the server:

```bash
python manage.py runserver
```

Admin credentials:

- User: `admin`
- Email: `admin@example.com`
- Password: `FetchReceipt`

Visit the same API URLs as listed above.
