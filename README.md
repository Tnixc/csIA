# IceSharkey's CS IA

# Todo

- [ ] make transcription feature use Whisper API
- [ ] Integrate Llama 3.2 3b for tagging call recordings (and translate?)
- [ ] Report page with filtering and data visualization (via tags + date)
    - [ ] Charts
    - [ ] Tables
- [ ] Manage page for administrators
    - [ ] change roles of other users
    - [ ] delete recordings
    - [ ] Show full transcription of selected call + info
- [ ] user role-based access control (for 'manage')

# run

This project uses [uv](https://github.com/astral-sh/uv). You will need to set up a `.env` in the root with the following variables:

```
SECRET_KEY=GOCSPX-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_CLIENT_ID=000000000000-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
```

Then run:

```bash
uv run run.py
```
