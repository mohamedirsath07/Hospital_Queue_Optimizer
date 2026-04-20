# 📸 National Showcase - Screenshot & Presentation Guide

## Overview
This guide helps you capture professional screenshots of the AI Hospital Triage System for the national showcase website.

---

## 📹 Screenshots to Capture

### 1. **Hero Shot** - Empty Application
**What**: The app homepage ready for user input
**Purpose**: First impression, shows clean UI design

**How to capture:**
- Open https://hospital-queue-optimizer-xi.vercel.app/
- Wait for full load
- Scroll to top
- Take full page screenshot
- Size: 1920x1080 (desktop), 375x812 (mobile)

**Filename**: `1_hero_home.png`

---

### 2. **Symptom Input** - With Example Text
**What**: User entering symptoms (pre-filled example)
**Purpose**: Shows the input interface and UX

**How to capture:**
- Click in the symptom textarea
- Type: "Severe chest pain radiating to my left arm with shortness of breath"
- Take screenshot before clicking analyze
- Highlight the character counter and quick scenario buttons
- Size: 1920x1080

**Filename**: `2_symptom_input.png`

---

### 3. **Loading State** - Spinner Animation
**What**: The app analyzing symptoms (loading spinner)
**Purpose**: Shows AI processing in action

**How to capture:**
- Enter any symptoms
- Click "Analyze Symptoms"
- Immediately screenshot the loading spinner/overlay
- Size: 1920x1080

**Filename**: `3_loading_state.png`

---

### 4. **Critical Result** - Eye-Catching Red Alert
**What**: Critical priority classification with escalation warnings
**Purpose**: Most dramatic output, shows urgency levels

**How to capture:**
- Use this symptom: "Severe chest pain radiating to left arm, shortness of breath"
- Click "Analyze"
- Once results load, screenshot the priority card (red color critical)
- Capture the escalation warnings section
- Size: 1920x1080

**Filename**: `4_critical_result.png`

---

### 5. **Hospital Recommendations** - Map Integration
**What**: Hospital results with distance, rating, call buttons
**Purpose**: Shows second key feature (hospital finding)

**How to capture:**
- After getting results, allow location access (or use any location)
- Scroll down to hospital recommendations section
- Screenshot showing 3-4 hospital cards with:
  - Hospital name
  - Distance
  - Navigation button
  - Call button
- Size: 1920x1080

**Filename**: `5_hospitals_list.png`

---

### 6. **Mobile View** - Responsive Design Demo
**What**: App on mobile device (375px width)
**Purpose**: Shows cross-device compatibility

**How to capture:**
- Open DevTools (F12)
- Set to mobile view (375x812)
- Go through flow: input → results → hospitals
- Take screenshots showing:
  - Mobile home (375x812)
  - Mobile results (375x812)
  - Mobile hospitals (375x812)
- Size: 375x812

**Filenames**: 
- `6_mobile_home.png`
- `7_mobile_results.png`
- `8_mobile_hospitals.png`

---

### 7. **Feature Highlights** - Info Cards
**What**: The explanation cards showing how priority is determined
**Purpose**: Educates about system logic

**How to capture:**
- From results page, scroll to info cards section
- Screenshot showing cards like:
  - "Priority Classification"
  - "Escalation Triggers"
  - "Hospital Matching Algorithm"
- Size: 1920x1080

**Filename**: `9_feature_cards.png`

---

### 8. **Success Case** - Non-Critical Results
**What**: Example of non-urgent case
**Purpose**: Shows system handles all priority levels

**How to capture:**
- Enter: "Mild headache for 2 hours"
- Get results showing non-urgent priority (green)
- Screenshot showing green color for low priority
- Size: 1920x1080

**Filename**: `10_low_priority_result.png`

---

## 🎥 Screenshots Summary Table

| # | Name | File | Purpose | Size |
|---|------|------|---------|------|
| 1 | Hero Shot | `1_hero_home.png` | First impression | 1920x1080 |
| 2 | Symptom Input | `2_symptom_input.png` | Input interface | 1920x1080 |
| 3 | Loading State | `3_loading_state.png` | AI processing | 1920x1080 |
| 4 | Critical Result | `4_critical_result.png` | Red alert demo | 1920x1080 |
| 5 | Hospitals | `5_hospitals_list.png` | Map integration | 1920x1080 |
| 6-8 | Mobile Views | `6,7,8_mobile_*.png` | Responsive design | 375x812 |
| 9 | Features | `9_feature_cards.png` | System logic | 1920x1080 |
| 10 | Low Priority | `10_low_priority_result.png` | Normal cases | 1920x1080 |

---

## 🎨 Screenshot Best Practices

### Quality Standards
- ✅ **Resolution**: Minimum 1920x1080 for desktop, 375x812 for mobile
- ✅ **Format**: PNG (lossless quality)
- ✅ **Clarity**: No blur, artifacts, or mouse cursor visible
- ✅ **Lighting**: Screen brightness at 100% for web apps
- ✅ **Timing**: Wait 1-2 seconds after actions for full load

### What to Include
- ✅ Full application interface
- ✅ Header with logo and title
- ✅ All interactive elements visible
- ✅ Text completely readable
- ✅ Color coding visible (priority colors)

### What to Avoid
- ❌ Personal information visible
- ❌ Error messages or failures
- ❌ Browser address bar (crop if needed)
- ❌ Incomplete loading states
- ❌ Blurry or low-res images
- ❌ Personal browser tabs visible
- ❌ Operating system taskbar in shot

---

## 📱 Tools for Screenshots

### On Windows
- **Built-in**: Windows + Shift + S (Snip & Sketch)
- **Tools**: Snagit, Greenshot, ShareX
- **Browser**: F12 → Device Toolbar → Take screenshot

### On Mac
- **Built-in**: Cmd + Shift + 4 (rectangular selection)
- **Tools**: Skitch, CleanMyMac's capture tool
- **Browser**: Safari → Develop → Take Screenshot

### Browser DevTools
1. Open DevTools (F12)
2. Toggle Device Toolbar (Ctrl+Shift+M)
3. Set device/size
4. Cmd/Ctrl + Shift + P → "Capture Screenshot"
5. Full page or viewport

---

## 🖼️ Creating a Screenshot Collection

### Folder Structure
```
/project_root/
├── /docs/
│   ├── /screenshots_raw/
│   │   ├── 1_hero_home.png
│   │   ├── 2_symptom_input.png
│   │   ├── 3_loading_state.png
│   │   └── ... (8 more)
│   └── screenshots_showcase.md (this file)
```

### Rename Consistently
Use format: `[number]_[descriptor].png`
Examples:
- `1_hero_home.png` ✅
- `2_symptom_input.png` ✅
- `screenshot_home_page.png` ❌ (inconsistent naming)

---

## 📝 Creating Screenshots Document

After capturing, create `SCREENSHOTS.md` with:

```markdown
# AI Hospital Triage System - Screenshots

## 1. Home Screen
![Hero Shot](docs/screenshots/1_hero_home.png)
*Clean interface ready for symptom input*

## 2. Input Example
![Symptom Input](docs/screenshots/2_symptom_input.png)
*User enters symptoms with character counter*

## 3. Critical Alert
![Critical Result](docs/screenshots/4_critical_result.png)
*System shows critical priority in red with warnings*

... (continue for all screenshots)
```

---

## 🎬 Video Demo (Optional Enhancement)

If you want to create a short demo video:

**Duration**: 60-90 seconds
**Content**: 
1. Home screen (5 sec)
2. Enter symptoms (10 sec)
3. Results appear (15 sec)
4. Show hospitals (20 sec)
5. Click hospital (10 sec)
6. Outro with summary (10-20 sec)

**Tools**: 
- CapCut (easy, free)
- OBS Studio (professional)
- ScreenFlow (Mac)
- Camtasia (premium)

---

## ✅ Pre-Submission Checklist

Before submitting screenshots:

- [ ] All 8-10 screenshots captured
- [ ] Files named consistently (number_descriptor.png)
- [ ] All PNG format, high quality
- [ ] No personal data visible
- [ ] No error states shown
- [ ] Mobile views at correct resolution
- [ ] Desktop views at 1920x1080 minimum
- [ ] Text readable in all screenshots
- [ ] Colors displaying correctly
- [ ] Screenshots placed in `/docs/screenshots/` folder
- [ ] `SCREENSHOTS.md` created with captions
- [ ] Proof-read image captions

---

## 🎯 Tips for Showcase Impact

### Make Screenshots Tell a Story
1. **First impression** (hero)
2. **How to use it** (input)
3. **AI in action** (loading)
4. **Critical case** (red alert)
5. **Full solution** (hospitals)
6. **Works everywhere** (mobile)

### Highlight Key Features
- ✨ Beautiful dark theme
- 🎯 Clear priority colors
- 🗺️ Integrated hospital finding
- 📱 Responsive design
- ⚡ Fast responses

### Professional Polish
- Consistent sizing and framing
- High contrast for readability
- All text visible and clear
- Color coding obvious
- No distracting elements

---

## 📧 Screenshot Submission

**Include with your submission:**
1. All 8-10 screenshots in folder: `docs/screenshots/`
2. File: `SCREENSHOTS.md` with descriptions
3. Optional: 60-second demo video

**Email attachment size**: ~5-10 MB total

---

## 🆘 Troubleshooting

**Screenshot is blurry?**
- Increase screen zoom (Ctrl/Cmd + Plus)
- Use Firefox/Chrome (better scaling)
- Try browser DevTools capture

**Colors look wrong?**
- Check monitor color profile
- Adjust brightness/contrast
- Try different browser

**Text too small?**
- Increase browser zoom to 125%
- Take screenshot at larger resolution
- Use Retina/High DPI setting

**Can't access the app?**
- Check deployment URLs are live
- Try incognito/private browser mode
- Clear browser cache (Ctrl+Shift+Del)

---

**Last Updated**: April 20, 2026
**Ready for**: National Showcase Submission

Good luck! 📸✨
