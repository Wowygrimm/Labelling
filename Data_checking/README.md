# Cleaning process

**Initial source file:** `part_x_raw.csv`

**Data format:**
- `TRIAL_INDEX` = Value between 1 and 18
- `EYE_USED` = Always *"RIGHT"*
- `CURRENT_FIX_X` = Float values (X,X)
- `CURRENT_FIX_Y` = Float values (X,X)
- `CURRENT_FIX_START` = Integer
- `CURRENT_FIX_DURATION` = Integer
- `CURRENT_FIX_BLINK_AROUND` = *"NONE"*, *"BEFORE"* or *"AFTER"*
- `NEXT_SAC_END_X` = Float values (X,X)
- `NEXT_SAC_END_Y` = Float values (X,X)
- `NEXT_SAC_AMPLITUDE` = Float values (X,X) or *"."*
- `NEXT_SAC_DIRECTION` = *"LEFT"*, *"RIGHT"*, *"DOWN"*, *"UP"* or *"."*
- `NEXT_SAC_DURATION` = Integer
- `NEXT_SAC_ANGLE` = Float values (X,X) or *"."*
- `NEXT_SAC_AVG_VELOCITY` = Float values (X,X) or *"."*
- `NEXT_SAC_CONTAINS_BLINK` = *"true"* or *"false"*
- `NEXT_SAC_BLINK_START` = Integer
- `NEXT_SAC_BLINK_END` = Integer
- `NEXT_SAC_BLINK_DURATION` = Integer


# 0. Building datasets
**Input:** `part_x_raw.csv`

**Output:** `part_x_built.csv`, `part_x_scroll.csv` and `part_x_mouse_browser.csv`

**Process:**
- Clean columns by removing *"."* values and convert to right type
- Add `PART_ID` to dataset
- Load to DF mouse and scroll events from JSON
- Extract Datetimes from datasets and set to same format
- Sync timestamps/dates of all datasets using `_msg.csv` file
- Add `WEBSITE_ID` to dataset
- Add `CONDITION` to dataset
- Add `TASK` to dataset
- Add `DISTRACTOR` to dataset

# 1. Space bar
**Input:** `part_x_raw.csv`

**Output:** `part_x_no_tail.csv`

**Process:**
- Delete the two last seconds of every trials in Target Finding condition (2, 4 and 6)
- Delete every rows starting from the bottom which are outside the bottom of the screen and stop when there is two consecutive rows within the screen

# 2. Clean blinks
**Input:** `part_x_no_tail.csv`

**Output:** `part_x_no_blink.csv`

**Process:**
- Delete fixations under 120ms around blinks
- Remove blink on Time axis
- Delete last saccade event for each trial
- Recompute `NEXT_SAC_AMPLITUDE` and `NEXT_SAC_DIRECTION`

# 3. Clean outsiders
**Input:** `part_x_no_blink.csv`

**Output:** `part_x_no_outsider.csv`

**Process:**
- Delete fixations further than 3 degrees (105px)
- Adjust fixations within 3 degrees of the screen to screen's limits
- Recompute `NEXT_SAC_AMPLITUDE` and `NEXT_SAC_DIRECTION`


# 4. Check data consistancy
**Input:** `part_x_no_outsider.csv`

**Output:** `matrix_trials.csv` and `trials_droplist.csv`

**Process:**
- Ensure there is 18 `TRIAL_INDEX`
- Ensure `CURRENT_FIX_X` and `CURRENT_FIX_Y` are positives and in the 1920x1080 screen
- Ensure `CURRENT_FIX_START` is positive
- Ensure `EYE_USED` is always equal to *"RIGHT"*
- Ensure `CURRENT_FIX_DURATION` is positive
- Ensure there is 18 `WEBSITE_ID`
- Ensure there is 6 x 3 `CONDITION`


# 5. Drop trials
**Input:** `part_x_no_blink.csv` and `trials_droplist.csv`

**Output:** `part_x_drop.csv`

**Process:**
- Delete trials listed in `trials_droplist.csv`
- Add `CALIBRATION_PROBLEM` to dataset. Values are *"No"* or *"Yes"*
- Delete trials with perturbations
