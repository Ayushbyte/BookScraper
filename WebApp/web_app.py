from flask import Flask, render_template, jsonify, send_file
from App import get_all_book_links, scrape_book_details, save_to_csv
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape')
def scrape():
    category_url = "https://notionpress.com/in/store/categories/cooking-food-wine/"
    book_urls = get_all_book_links(category_url, target_count=100)
    
    book_details_list = []
    for url in book_urls:
        try:
            details = scrape_book_details(url)
            if details:
                book_details_list.append(details)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # Save to CSV
    save_to_csv(book_details_list)
    
    return jsonify({"books": book_details_list})

@app.route('/download')
def download():
    return send_file('book_details.csv',
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='book_details.csv')

if __name__ == '__main__':
    app.run(debug=True)