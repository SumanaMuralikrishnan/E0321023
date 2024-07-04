from flask import Flask, jsonify, request
from collections import deque
import requests

app = Flask(__name__)

# Defined the window size
WINDOW_SIZE = 10

# Defined the number IDs and their corresponding third-party API URLs
NUMBER_ENDPOINTS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'r': 'http://20.244.56.144/test/random'
}

# In-memory storage for numbers using deque to maintain window size
numbers = {number_id: deque(maxlen=WINDOW_SIZE) for number_id in NUMBER_ENDPOINTS}

# Authentication token
AUTH_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzIwMDgxMjQ0LCJpYXQiOjE3MjAwODA5NDQsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImEyNWM0ZmE1LWNjOWYtNDc2ZC1hZDBmLTRiMTNmYmJmZWQxNSIsInN1YiI6InN1bWFuYW11cmFsaWtyaXNobmFuQGdtYWlsLmNvbSJ9LCJjb21wYW55TmFtZSI6IlN0eWx1cyIsImNsaWVudElEIjoiYTI1YzRmYTUtY2M5Zi00NzZkLWFkMGYtNGIxM2ZiYmZlZDE1IiwiY2xpZW50U2VjcmV0IjoiVG9xTmVFUFRqaElWRUxWWCIsIm93bmVyTmFtZSI6IlN1bWFuYSIsIm93bmVyRW1haWwiOiJzdW1hbmFtdXJhbGlrcmlzaG5hbkBnbWFpbC5jb20iLCJyb2xsTm8iOiJFMDMyMTAyMyJ9.TQf6osu_lzCdEKr-rwXn2exj-8gkzRHSxmRt5aMj1EY'

@app.route('/numbers/<string:number_id>', methods=['GET', 'POST'])
def handle_number(number_id):
    if number_id not in NUMBER_ENDPOINTS:
        return jsonify({'error': 'Invalid number ID'}), 400

    if request.method == 'GET':
        # Return the current state, input, and average
        current_state = list(numbers[number_id])
        prev_state = current_state[:-1] if current_state else []
        avg = sum(current_state) / len(current_state) if current_state else 0
        return jsonify({
            'windowprevstate': prev_state,
            'currentstate': current_state,
            'input': None,  
            'average': avg
        })

    elif request.method == 'POST':
        try:
            # Fetch number from third-party API
            headers = {'Authorization': AUTH_TOKEN}
            response = requests.get(NUMBER_ENDPOINTS[number_id], headers=headers)

            if response.status_code != 200:
                return jsonify({'error': f'Failed to fetch number from {number_id} endpoint'}), 500

            num = response.json().get('number')

            # Add the new number to the window
            numbers[number_id].append(num)

            # Calculate average
            current_state = list(numbers[number_id])
            prev_state = current_state[:-1] if current_state else []
            avg = sum(current_state) / len(current_state) if current_state else 0

            # Return the updated state, input, and average
            return jsonify({
                'windowprevstate': prev_state,
                'currentstate': current_state,
                'input': num,
                'average': avg
            })

        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Request to {number_id} endpoint failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)