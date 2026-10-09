from flask import Flask, render_template, request

app = Flask(__name__)


def reduce_to_single_digit(value: int) -> int:
    while value > 9:
        value = sum(int(digit) for digit in str(value))
    return value


def calculate_birth_number(day: int) -> int:
    return reduce_to_single_digit(day)


def calculate_solar_number(birth_number: int, month: int) -> int:
    return reduce_to_single_digit(birth_number + month)


def calculate_year_number(year: int) -> int:
    return reduce_to_single_digit(year)


def calculate_life_path_number(birth_number: int, solar_number: int, year_number: int) -> int:
    return reduce_to_single_digit(birth_number + solar_number + year_number)


@app.route('/', methods=['GET', 'POST'])
def index():
    profile = None
    error = None

    if request.method == 'POST':
        date_text = request.form.get('birth_date', '').strip()
        try:
            year, month, day = map(int, date_text.split('-'))
            birth_number = calculate_birth_number(day)
            year_number = calculate_year_number(year)
            solar_number = calculate_solar_number(birth_number, month)
            life_path_number = calculate_life_path_number(birth_number, solar_number, year_number)

            profile = {
                'birth_number': birth_number,
                'solar_number': solar_number,
                'life_path_number': life_path_number,
                'year_number': year_number,
            }
        except ValueError:
            error = 'لطفاً تاریخ تولد را در قالب YYYY-MM-DD وارد کنید.'

    return render_template('index.html', profile=profile, error=error)


if __name__ == '__main__':
    app.run(debug=True)
