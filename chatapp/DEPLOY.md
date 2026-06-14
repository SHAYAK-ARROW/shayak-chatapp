# Deploy Guide (Render + Supabase)

## Step 1: GitHub e code push kora

1. github.com e notun repository banao (e.g. `chatapp`)
2. tomar `chatapp` folder er shob file push kore dao

```
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/<tomar-username>/chatapp.git
git push -u origin main
```

## Step 2: Render e deploy

1. render.com e jao, GitHub diye sign up koro (card lagbe na)
2. **New +** -> **Web Service** click koro
3. tomar github repo select koro
4. Settings:
   - **Name:** jeta chao (e.g. chatapp)
   - **Root Directory:** jodi `chatapp` folder er bhitore amar code thake (e.g. `chatapp/chatapp`), tahole eta set koro. Na hole blank rakho
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -k eventlet -w 1 main:app`
   - **Instance Type:** Free

## Step 3: Environment Variable set kora (Supabase DB)

Render dashboard e tomar service -> **Environment** tab e jao, ekta notun variable add koro:

```
Key:   DATABASE_URL
Value: postgresql://postgres:<TOMAR-PASSWORD>@db.czkzwjaqikosultupvwy.supabase.co:5432/postgres
```

`<TOMAR-PASSWORD>` er jaygay Supabase project banar somoy je password disilo, ta bosao.

## Step 4: Deploy

**Create Web Service** / **Manual Deploy** click korle Render build & start kore debe.
2-5 minute lagte pare. Build successful hole ekta URL pabe
(e.g. `https://chatapp.onrender.com`) - ei link e gele app open hobe.

## Note (Important)

- Render free tier: app 15 min inactive thakle "sleep" hoye jay,
  abar request gele 30-50 sec por start hoy. Eta normal, kono error na.
- Supabase free tier: 1 week inactive thakle project "pause" hoy.
  Supabase dashboard e gie **Resume Project** click korle abar active hobe,
  data thekei jabe.
