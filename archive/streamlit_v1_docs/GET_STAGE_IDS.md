# Get Stage IDs - Simple 5-Minute Guide

The GHL API doesn't expose pipeline endpoints, so we need to extract stage IDs from the browser.

## Option 1: JavaScript Console (EASIEST - 2 minutes)

1. **Open your pipeline edit page** in GHL:
   ```
   https://app.getaireview.com/v2/location/BUBjaBnB1qp6NfrTYYoo/opportunities/pipeline?mode=update&id=ZHnsDZ6eQJYvnxFR0DMU
   ```

2. **Open Developer Console**:
   - Press **F12** (or **Cmd+Option+I** on Mac)
   - Click the **Console** tab

3. **Paste this JavaScript** and press Enter:
   ```javascript
   // Find all stage inputs
   const stages = {};
   document.querySelectorAll('input[name*="stage"], input[value*="Lead"], input[value*="Review"], input[value*="Scheduled"], input[value*="Submitted"], input[value*="Contract"], input[value*="Won"], input[value*="Lost"]').forEach(el => {
     const value = el.value;
     const name = el.name || el.getAttribute('data-name') || el.id;
     if (value && value.length > 10) {
       console.log(`${value}: ${name}`);
       stages[value] = name;
     }
   });

   // Also check for data attributes
   document.querySelectorAll('[data-stage-id], [data-id]').forEach(el => {
     const stageId = el.getAttribute('data-stage-id') || el.getAttribute('data-id');
     const text = el.textContent || el.innerText;
     if (stageId && stageId.length > 10 && text && text.match(/Lead|Review|Scheduled|Submitted|Contract|Won|Lost/)) {
       console.log(`${text.trim()}: ${stageId}`);
     }
   });

   console.log('---');
   console.log('Copy the IDs above and send them to me!');
   ```

4. **Copy the output** and send it to me

---

## Option 2: Network Tab (3 minutes)

1. **Open Developer Tools** (F12 or Cmd+Option+I)

2. **Click the Network tab**

3. **Click "Update" button** on the pipeline edit dialog

4. **Look for API calls** - find one that includes your pipeline ID

5. **Click on it** → **Preview/Response** tab

6. **Look for "stages" array** with IDs

7. **Take screenshot** and send to me

---

## Option 3: Just Tell Me The Stage Names (1 minute)

If the above doesn't work, we can work around it!

Just tell me "I can see the stages" and I'll create a workaround where:
- We create a test opportunity
- It auto-assigns to first stage
- We get that stage ID
- Then we manually move it through stages
- Get each stage ID as we go

---

## What I Need

Send me **any one** of these:

1. ✅ **Output from JavaScript console**
2. ✅ **Screenshot of Network tab API response**
3. ✅ **Screenshot of HTML inspector showing stage elements**
4. ✅ **Just say "let's try the workaround"** and I'll guide you

---

**Don't worry if this seems complicated - any of these options will work, and I'll walk you through it!**
