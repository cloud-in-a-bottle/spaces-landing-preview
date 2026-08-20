# spaces-landing-preview

A standalone **styling preview** for the idea in the imbue-hosted-spaces note:
take a pass at the real Cloud in a Bottle look, and merge the landing page and
the "choose your space" plan picker into a single page — since anyone who lands
here arrived from the "Managed by Imbue" button on cloudinabottle.org and
already wants a managed space.

**This is not the live site.** It touches nothing in
`cloud-in-a-bottle/imbue-hosted-spaces`. It's a throwaway app meant to be
deployed to a Cloud in a Bottle instance for review and iteration. The plan
buttons don't provision anything.

The styling (fonts, colors, pixel/8-bit components, dithered horizons) is
lifted from cloudinabottle.org so the pass is faithful; the plan sizes and
prices mirror the real app's catalog (Small/Medium/Large at $5/$10/$20).

## Run locally

```bash
pip install .
uvicorn preview.app:app --host 0.0.0.0 --port 8080
# open http://localhost:8080
```

## Deploy to a Cloud in a Bottle instance

```bash
oh app deploy <git-url-of-this-repo>
```

`openhost.toml` publishes it on port 8080 with a public `/` and a `/health`
check.
