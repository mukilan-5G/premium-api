#!flask/bin/python
import json
import scipy.interpolate
from flask import Flask, jsonify, request

app = Flask(__name__)

base_premium = 350

dwelling_coverage_factors = {}
with open('rating_factors/dwelling_coverage_factors.json') as json_file:  
	dwelling_coverage_factors = json.load(json_file)

home_age_factors = {}
with open('rating_factors/home_age_factors.json') as json_file:  
	home_age_factors = json.load(json_file)

roof_type_factors = {}
with open('rating_factors/roof_type_factors.json') as json_file:  
	roof_type_factors = json.load(json_file)      

unit_factors = {}
with open('rating_factors/unit_factors.json') as json_file:  
	unit_factors = json.load(json_file)


# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def get_home_age_factor(home_age):
	home_age = int(home_age)
	for age_range, factor in home_age_factors.iteritems():
		age_range_list = age_range.split('-')
		if len(age_range_list) > 1:
			start, end = tuple(int(x) for x in age_range.split('-'))
			if start < home_age and home_age < end:
				return factor
		else:
			if home_age >= int(age_range_list[0]):
				return factor


def get_dwelling_coverage_factor(dwelling_coverage):
	y_interp = scipy.interpolate.interp1d(
		[int(x) for x in dwelling_coverage_factors.keys()], dwelling_coverage_factors.values()) 
	return round(y_interp(int(dwelling_coverage)), 3)



@app.route('/api/premium', methods=['POST'])
def get_quoted_premium():
	if not request.json or not 'customer_requests' in request.json:
		abort(400)

	response = {"final_quoted_premium_amount": {}}
	for customer, reqString in request.json["customer_requests"].iteritems():
		reqList = [str(x) for x in reqString.split('+')]
		quoted_monthly_premium = base_premium * get_dwelling_coverage_factor(reqList[0]) * get_home_age_factor(reqList[1]) * roof_type_factors[reqList[2]] * unit_factors[reqList[3]] 
		discounted_amount = quoted_monthly_premium * (0.05 if reqList[4] == "Y" else 0)
		final_quoted_premium_amount = quoted_monthly_premium - discounted_amount
		response["final_quoted_premium_amount"][customer] = round(final_quoted_premium_amount)
		print customer, final_quoted_premium_amount
	return jsonify(response)

if __name__ == '__main__':
	app.run(debug=True)
