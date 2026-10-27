# Mikvah directory

`mikvaos.json` is the women's mikvah directory used by the Mikvah app. It is built from the
public directory at https://mikvah.org/directory and served from GitHub Pages at

    https://tsuriele.github.io/mikvah-directory/mikvaos.json

The app ships a bundled copy and refreshes from this URL, so updating the file here updates
every installed app without a release.

## Updating

```
python3 scripts/crawl.py          # fetches each listing's detail page into details/ (resumable)
python3 scripts/build_dataset.py mikvaos.json
```

`crawl.py` expects a `base.json` (the directory's map listing) next to it. Only women's mikvaos are
kept: entries whose name says keilim, men's or vessels are dropped. Review any new entries before
committing; a listing here is read as a women's mikvah by the app.
