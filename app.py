from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods = ['GET', 'POST'])
def index():
	if request.method == 'GET':
  		return render_template('index.html')
	else: 
		char_chosen_list = []
		for char in ['med_hhld_inc', 'white_only_pct', 'black_only_pct', 
				'asian_only_pct', 'mixed_races_pct', 'hhld_size_all', 'noise_res', 
				'assault', 'drug', 'harrassment', 'rape_sex_crime', 'robbery', 
				'theft', 'weapon', 'healthy_trees']:
			if request.form.get(char): 
				char_chosen_list.append(request.form.get(char))
		return render_template('picked_chars.html', char_chosen_list = char_chosen_list)
  		
@app.route('/picked_vals', methods = ['POST', 'GET'])
def picked_vals():
	if request.method == 'POST':
		picked_vals_results = request.form
		return render_template("picked_vals.html", picked_vals_results = picked_vals_results)

if __name__ == '__main__':
	app.run(port=33507)
