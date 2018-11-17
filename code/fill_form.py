import json
import pyautogui
import time

time.sleep(2)
with open('fill.json', 'r') as f:
    req_dict = json.load(f)

# Enter email
pyautogui.click(req_dict['email_pos'][0], req_dict['email_pos'][1])
pyautogui.typewrite('jarraramjad@gmail.com')

# Enter Public key
pyautogui.click(req_dict['pub_pos'][0], req_dict['pub_pos'][1])
pyautogui.typewrite('ETT91dKTKwaC0LyWLl5F2zR2iW8NC8e6R0oLwayY3poRyC7rmN4LBxUE29RTg6xz')

# Enter Private key
pyautogui.click(req_dict['pri_pos'][0], req_dict['pri_pos'][1])
pyautogui.typewrite('04J6CvryREZ09BGUQmbqkj1iyzdPBI1XNvWqYdImthqeqFoxC9LrFneycLyS1JTP')

# Enter SMA-20
pyautogui.click(req_dict['sma_20_pos'][0], req_dict['sma_20_pos'][1])
pyautogui.typewrite('20')

# Enter SMA-50
pyautogui.click(req_dict['sma_50_pos'][0], req_dict['sma_50_pos'][1])
pyautogui.typewrite('50')

# Enter TP
pyautogui.click(req_dict['tp_pos'][0], req_dict['tp_pos'][1])
pyautogui.typewrite('10')

# Enter radio button
pyautogui.click(req_dict['radio_btn_pos_1'][0], req_dict['radio_btn_pos_1'][1])

# Enter tf1
pyautogui.click(req_dict['t1_pos_1'][0], req_dict['t1_pos_1'][1])
pyautogui.click(req_dict['t1_pos_2'][0], req_dict['t1_pos_2'][1])

# Enter tf2
pyautogui.click(req_dict['t2_pos_1'][0], req_dict['t2_pos_1'][1])
pyautogui.click(req_dict['t2_pos_2'][0], req_dict['t2_pos_2'][1])

# Enter tf3
pyautogui.click(req_dict['t3_pos_1'][0], req_dict['t3_pos_1'][1])
pyautogui.click(req_dict['t3_pos_2'][0], req_dict['t3_pos_2'][1])

# Enter var_quote_1
pyautogui.click(req_dict['var_quote_pos_1'][0], req_dict['var_quote_pos_1'][1])
pyautogui.click(req_dict['var_quote_pos_2'][0], req_dict['var_quote_pos_2'][1])

# Enter amt_coins
pyautogui.click(req_dict['coin_amt_pos_1'][0], req_dict['coin_amt_pos_1'][1])
pyautogui.click(req_dict['coin_amt_pos_2'][0], req_dict['coin_amt_pos_2'][1])

time.sleep(0.5)

# Click on save btn
pyautogui.click(req_dict['final_pos'][0], req_dict['final_pos'][1])
