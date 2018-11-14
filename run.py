import sys
from nightowl.app import app
from instance import insert_test_data

if __name__ == '__main__':
	if len(sys.argv) == 2:		
		if sys.argv[1] == 'insert_test_data':			
			insert_test_data.loadTestData()        
	else:		
		app.run()