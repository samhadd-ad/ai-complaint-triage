# Model results

- Emails: 1150 (train 847, test 303)
- Random-split accuracy: 100.0% (optimistic: shares sentence templates with training)
- **Accuracy on unseen wording: 67.0%** (whole templates held out)
- **Urgency rule accuracy: 98.6%**

## Per-category scores
```
                  precision    recall  f1-score   support

   Billing Issue      0.963     0.413     0.578        63
  Booking Change      0.608     0.814     0.696        59
      Compliment      1.000     0.611     0.759        36
Driver Behaviour      0.938     0.811     0.870        37
     Late Pickup      0.796     0.582     0.672        67
       Lost Item      0.404     0.927     0.563        41

        accuracy                          0.670       303
       macro avg      0.785     0.693     0.689       303
    weighted avg      0.783     0.670     0.677       303
```

## Words that drive each category
- **Billing Issue:** price, charge, card, extra, paid, receipt
- **Booking Change:** booking, reservation, hour earlier, ride hour, hour, earlier
- **Compliment:** appreciated, friendly, clean, car clean, time book, hi great
- **Driver Behaviour:** hi driver, driver, driving, speeding highway, speeding, ride speeding
- **Late Pickup:** late, minutes, came, showed, cab, arrivals
- **Lost Item:** left, forgot, bag, hi left, check, check driver
