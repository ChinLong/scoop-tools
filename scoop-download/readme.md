# Scoop Download

Scoop-download is a downloader to download app from mirror site. 

### How to user it.

- Add  scoop-customize bucket.
```shell script
scoop bucket add customize https://github.com/ChinLong/scoop-customize.git
```

- Install scoop-download
```shell script
scoop install scoop-download
```

- Download scoop app.
```shell script
scoop-download maven git
```

- Install app.
```shell script
scoop install maven git
```

### How to set mirror.
- Open `conf/mirror.json`

```json
{
  "sample-name": {
    "origin_host": "sample-origin",
    "mirror_host": "sample-mirror",
    "support_apps": [
      "sample-app"
    ]
  }
}
```
- Add or replace sample attr.



