from __future__ import print_function
import sys
from datetime import datetime
import bisect
from utils import get_percentile


class Parser():
    def __init__(self, percentile_file):
        self.donors = {}
        self.recipients = {}
        with open(percentile_file, 'r') as f:
            self.percentile = int(f.read().strip())
        print("Using percentile = {}%".format(self.percentile))
        
    def __call__(self, input_file, output_file, verbose=False, n_lines=None):
        """Main function to parse lines
        Args:
            input_file (string) : input file
            output_file (string) : output_file
            verbose (bool) : if True, displays each parsed entry
            n_lines (int) : number of lines to read from start 
                            (default=None reads all lines) 
        """
        counter = 0
        with open(input_file, 'r') as in_file, open(output_file, 'w') as out_file:
            for line in in_file:
                l = self.parse_line(line)
                if l:
                    output = self.add_update_donor(*l)
                    if output:
                        out_file.write(output)
                if verbose:
                    print(l)
                if n_lines:
                    counter += 1
                    if counter > n_lines:
                        break
            
    def parse_line(self, line):
        """Parses line to extract relevant fields
        Args:
            line (string) : raw input line read from input file
        Returns:
            tuple (cmte id, name, zip code, date, amount)"""
        a = line.split('|')
        cmte_id = a[0]
        name = a[7]
        zip_code = a[10]
        trns_date = a[13]
        trns_amnt = a[14]
        other_id = a[15]
        first_name, last_name = None, None
        try:
            cmte_id = cmte_id.strip()
            name = name.strip()
            zip_code = zip_code[:5]
            trns_date = datetime.strptime(trns_date, '%m%d%Y').date()
            trns_amnt = int(round(float(trns_amnt)))
            other_id = other_id.strip()
        except:
            return None
        cmte_id_fail = cmte_id is ''
        name_fail = name is ''
        zip_code_fail = ((zip_code is '') or (len(zip_code) != 5) 
                         or (not zip_code.isdigit()))
        other_id_fail = other_id is not ''
        if cmte_id_fail or name_fail or zip_code_fail or other_id_fail:
            return None
        return cmte_id, name, zip_code, trns_date, trns_amnt
        
    def add_update_donor(self, recipient_id, name, zip_code, date, amnt):
        """Adds a new donor or updates an existing one
        Args:
            recipient_id (string) : ctme_id of recipient for donation
            name (string) : name of donor
            zip_code (string) : zip code (first 5 digits)
            date (datetime.date) : date of donation
            amnt (int) : donation amount
        Returns:
            output string line to be written to file,
            returns None if not a repeat donor"""
        donor_id = '-'.join((name, zip_code))
        if donor_id not in self.donors:
            self.donors[donor_id] = {'date': date}
        elif date >= self.donors[donor_id]['date']:
            self.donors[donor_id]['date'] = date
            year = date.year
            sorted_amnts = self.add_update_recipient(recipient_id, year, zip_code, amnt)
            percentile = get_percentile(sorted_amnts, self.percentile)
            sum_amnts = sum(sorted_amnts)
            n = len(sorted_amnts)
            output = (recipient_id, zip_code, str(year), str(percentile), 
                      str(sum_amnts), str(n))
            output = '|'.join(output) + '\n'
            return output
        return None
                
    def add_update_recipient(self, recipient_id, year, zip_code, amnt):
        """Adds a new recipient or updates an existing one
        Args:
            recipient_id (string) : ctme_id of recipient
            year (int) : year of donation
            zip_code (string) : zip code (first 5 digits)
            amnt (int) : donation amount
        Returns:
            a list containing sorted donation amounts"""
        sorted_amnts = [amnt]
        if recipient_id not in self.recipients.keys():
            entry = {(year, zip_code) : {'amounts': sorted_amnts}}
            self.recipients[recipient_id] = entry
        else:
            rec = self.recipients[recipient_id]
            if (year, zip_code) not in rec.keys():
                rec[year, zip_code] = {'amounts': sorted_amnts}
            else:
                sorted_amnts = rec[year, zip_code]['amounts']
                bisect.insort(sorted_amnts, amnt)
        return sorted_amnts


if __name__ == "__main__":
    input_file = sys.argv[1]
    percentile_file = sys.argv[2]
    output_file = sys.argv[3]
    p = Parser(percentile_file)
    p(input_file, output_file)

