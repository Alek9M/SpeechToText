
conference_whisper_prompt = """
В. - Всем привет! Вам необходимо транскрибировать групповой звонок, на котором обсуждают аюрведические темы. Справитесь?
1. - Конечно!
2. - Легко
1. - Это же как медицина?
В. - Да."""

podcast_prompt = """
Всем привет! Это мой подкаст о здоровье и аюрведе на канале в Telegram"""


dialogue_gpt_prompt = """
You are a text processor. Convert a Russian transcript of a group call about Ayurveda into a simple dialogue. 
Do NOT shorten nor condense, the output is expected to roughly equal the size of input. There is a  host, number the rest of participants. 
Each speaker's dialogue should start with a hyphen and their number, and only when the speaker changes. 
Keep the original meaning and adjust punctuation for clarity. 
The audio was split into parts so sometimes there's a repetition of speech next to each other, disregard those. 
The output should be in Russian. For example:

Участник 1: [текст]
Участник 2: [текст]

не добавляй заголовки частям

не разделяй разговор одного человека на несколько частей так: 
Хост: [текст] 
Участник 1: [текст] 
Участник 1: [текст] 
Участник 1: [текст] 
Хост: [текст]

вместо этого делай так: 
Хост: [текст] 
Участник 1: [текст] 
[текст] 
[текст] 
Хост: [текст]"""

monologue_gpt_prompt = """
You are a text processor. Convert a Russian transcript of a podcast about Ayurveda into a simple text. 
Do NOT shorten nor condense, the output is expected to roughly equal the size of input. 
Keep the original meaning and adjust punctuation for clarity. 
The audio was split into parts so sometimes there's a repetition of transcript next to each other, disregard those. 
Полученный текст должен быть на руском
"""