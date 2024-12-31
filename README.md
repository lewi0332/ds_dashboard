# ds_dashboard
Data Science Job hunt dashboard




#### Important files:

* `main.py` is the Dash application server
* `index.py` is the main file that runs the Dash application
* `.gcloudignore` is like `.gitignore` for GitHub, it tells GCP what not to upload
* `app.yaml` is used to run the Dash app on GCP using [gunicorn](https://gunicorn.org/), which is needed for GCP
* `requirements.txt` comprises the packages needed to run the Dash app (important: gunicorn is required in this file at the bare minimum)
* `assets` folder contains the images and fonts used in the Dash app
* `apps` folder contains the other Dash pages
  
## Running the App Locally

**Clone the repository**

Create the virtual environment and activate it:

```
conda env create -f environment.yml
conda activate dash
```

Add your bigquery credentials to the environment. From the command line I used:

```
gcloud auth application-default login
```

This opens a browser alloing you to give your local machine access to the GCP project. 

From the parent directory, run:

```
python index.py
```

If things are working correctly, this should print out:

```
Dash is running on http://0.0.0.0/8050/
```




## Deploying Application to Google Cloud Platform

**Make a Project on GCP**
  - Using the CLI or the Console Interface online (which we use below), create a new project with a suitable project name (here we call it `dash-example`).

**Make Yourself the Owner of Project**
- Make sure the project you've just created is selected on the console, then click 'ADD PEOPLE TO THIS PROJECT'.

**Deploy Using gcloud Command Line Tool**

If you haven't installed the [gcloud command line tool](https://cloud.google.com/sdk/gcloud/) do so now.

Next, check your project is active in gcloud using:

`gcloud config get-value project`

Which will print the following on screen:

```
Your active configuration is: [default]

my-project-id
```

To change the project to your desired project, type:

`gcloud config set project project-id`

Next, to deploy, type:

`gcloud app deploy`

Then select your desired region (`us-central1`)

If you have setup your configuration correctly then it will deploy the Dash app (after a while), which will be available at:

`https://project-id.appspot.com/`

The example app above is hosted [here](https://simple-dash-app-engine-app-dot-dash-example-265811.appspot.com/)

**Restrict Access to your Application**

By default your application will be accessible to anyone in the world. To restrict the access you can use [Firewall Rules](https://cloud.google.com/blog/products/gcp/introducing-app-engine-firewall-an-easy-way-to-control-access-to-your-app).

## Cloud Build

Cloud Build is a service that executes your builds on Google Cloud Platform infrastructure. Cloud Build can import source code from Google Cloud Storage, Cloud Source Repositories, GitHub, or Bitbucket, execute a build to your specifications, and produce artifacts such as Docker containers or Java archives.

After the app has been deployed, you can use Cloud Build to automatically deploy the app when you push to GitHub. This is done by creating a `cloudbuild.yaml` file in the root directory of your project. This file contains the instructions for Cloud Build to deploy your app.