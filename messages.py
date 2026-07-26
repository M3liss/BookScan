import random

GREETINGS = [
    "Hello", "Hiiii", "Ahoy", "Bonjour", "Ciao", "Hola", 
    "Salve", "Hej", "Whaddup", "Na"
]

FUN_RECOMMENDATIONS = [
    "Buy your awesome little sister TEN books next year!",
    "Why haven't you used the day and called Melissa?",
    "What does your little sister gotta do to GET A CALL???",
    "You're getting old. Read more.",
    "Try to read Les Misérables this month.",
    "Ew.",
    "Today is a day for smiling! Like the joker. Please don't kill me.",
    "Ask yourself today - why are you alive? Why is your little sister so much better than you? Have you ever been cool?"
]


RATIO_MESSAGES = {
    "very_low": [
        "Uuuuuhm. Honestly, don't you read?",
        "You have yet to feed your mind.",
        "YOu obviously don't know the definition of 'reading'. Of course, as you have never picked up a book.",
        "SHAAAAAAAAAAAAAAAAAAAAAAAAAAME",
        "One word: unacceptable. Start now!"
    ],
    "low": [
        "I'm still disappointed.",
        "If you were reading any slower you'd be going backwords.",
        "The books are obviously not your friends",
        "I mean, you have done something at least..."
    ],
    "medium": [
        "Alright, you are getting there!",
        "Maybe don't buy new books but start reading? Is that too much to ask?",
        "Congrats, I think you can call yourself literate!",
        "So many books yet to be read..."
    ],
    "high": [
        "Wow, I am actually impressed! Never thought you would be capable of this!",
        "You’ve read more than 80% of people this year. Probably. Maybe.",
        "I'm still cooler than you, but you're getting close.",
        "Psssst - the books fear you.",
        "DAAAAAAAAAAAAAAAAAAAAAAAAAAAAMN"
    ],
    "perfect": [
        "Do you want me to sign you up to Books Anonymous?"
        "I never knew you could read THIS WELL"
        "I dont think you'll ever read this. But I love you."
    ]
}


# --- Functions ---
def get_random_greeting():
    return random.choice(GREETINGS)

def get_random_recommendation():
    return random.choice(FUN_RECOMMENDATIONS)

def get_ratio_message(ratio):
    ratio = ratio * 100
    if ratio < 20:
        key = "very_low"
    elif ratio < 40:
        key = "low"
    elif ratio < 60:
        key = "medium"
    elif ratio < 90:
        key = "high"
    else:
        key = "perfect"

    return random.choice(RATIO_MESSAGES[key])
