from enum import Enum


# u'\U00000000'
class Emoji(Enum):
    digit_zero = u'\U00000030\U000020E3'
    digit_one = u'\U00000031\U000020E3'
    digit_two = u'\U00000032\U000020E3'
    digit_three = u'\U00000033\U000020E3'
    digit_four = u'\U00000034\U000020E3'
    digit_five = u'\U00000035\U000020E3'
    digit_six = u'\U00000036\U000020E3'
    digit_seven = u'\U00000037\U000020E3'
    digit_eight = u'\U00000038\U000020E3'
    digit_nine = u'\U00000039\U000020E3'


emoji_digits = [Emoji.digit_zero.value,
                Emoji.digit_one.value,
                Emoji.digit_two.value,
                Emoji.digit_three.value,
                Emoji.digit_four.value,
                Emoji.digit_five.value,
                Emoji.digit_six.value,
                Emoji.digit_seven.value,
                Emoji.digit_eight.value,
                Emoji.digit_nine.value]
