# cd-automation

### Must
- `pip install -r requirements.txt`

### How it works
1. Creates a fix version per the argument.
2. Associates the comma separated list of tickets provided to that version.
3. Creates a Code Deployment ticket in the given project.
4. Generates a Slack message.

### Usage
1. The program needs the environment variables named on the `.env.sample` to run; feel free to create an `.env` and ignore it in your `.gitignore`
2. optionally create a `.deployrc` file in JSON format to keep your variables stored.

Example usage:
`python3 jiraslackping.py --help`

Example usage:

```sh
python3 jiraslackping.py --version="6.0.3" --user="pazadi" --release="https://bamboo.ngeo.com/deploy/viewDeploymentVersion.action?versionId=81461465" --rollback="6.0.2" --project="NGPYS" --tickets="NGPYS-9613" --projectfriendly="Your Shot" --qa="@franco.venica" --tl="@payam.azadi" --sre="@carlos.castro" --outage="NONE"
```

This creates a fix version per the argument, associates the comma separated list of tickets provided to that version, creates a Code Deployment ticket in the given project, and generates a Slack message.

Example usage:

create a `.deployrc` in JSON format with the options as key-value pairs to avoid writing the same values every time, e.g.
```
{
  "projectfriendly": "Your Shot",
  "sre": "@carlos.castro"
  "qa": "@franco.venica",
  "tl": "@payam.azadi",
  "user": "pazadi",
  "project": "NGPYS",
  "release": "https://bamboo.ngeo.com/deploy/viewDeploymentVersion.action?versionId=81461465"
}
```
This key-value pairs will be overwritten with the CLI arguments if both exist; after that you can use the script like in the previous example but only with the modified data e.g.
```
python3 jiraslackping.py --version="6.0.3" --rollback="6.0.2"  --tickets="NGPYS-9613"
```
