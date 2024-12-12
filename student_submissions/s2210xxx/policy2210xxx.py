from policy import Policy
import numpy as np
from scipy.optimize import linprog
from scipy.optimize import milp
from scipy.optimize import LinearConstraint
from copy import deepcopy
import time

class Policy2210xxx(Policy):    
    def __init__(self, policy_id=1):
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        self.policy_id = policy_id
        self.optimal_patterns = []
        self.isComputing = True
        self.drawing_counter = -1
        self.drawing_data = []
        self.list_stocks = []
        self.list_products = []
        self.keys = []
        self.sub_optimal_patterns = []
        if policy_id == 1:
            self.sub_optimal_patterns = []
        else:
            self.stock_buckets = {}
            self.bucket_size = 10 
            self.indices_prods = []
            self.sorted_prods = []

    def get_action(self, observation, info):
        if(self.isComputing):
            self.isComputing = False
            self.drawing_counter += 1
            self.implement_policy(observation,info)                
            return {
                "stock_idx": self.drawing_data[self.drawing_counter]["stock_idx"],
                "size": self.drawing_data[self.drawing_counter]["size"],
                "position": self.drawing_data[self.drawing_counter]["position"]
            }
        else:
            self.drawing_counter += 1
            if(self.drawing_counter == len(self.drawing_data)):
                # self.isComputing = True
                self.drawing_counter = 0
                self.optimal_patterns = []
                self.drawing_data = []
                self.list_products = []
                self.list_stocks = []
                self.keys = []
                if self.policy_id == 1:
                    self.sub_optimal_patterns = []
                else:
                    self.stock_buckets = {}
                    self.bucket_size = 10
                    self.indices_prods = []
                    self.sorted_prods = []
                self.implement_policy(observation,info)
                return {
                    "stock_idx": self.drawing_data[self.drawing_counter]["stock_idx"],
                    "size": self.drawing_data[self.drawing_counter]["size"],
                    "position": self.drawing_data[self.drawing_counter]["position"]
                }
            else:
                return {
                    "stock_idx": self.drawing_data[self.drawing_counter]["stock_idx"],
                    "size": self.drawing_data[self.drawing_counter]["size"],
                    "position": self.drawing_data[self.drawing_counter]["position"]
                }

    def implement_policy(self,observation,info):
        # initial_prods = [{'size': np.array([]), 'quantity': None} for _ in range(len(observation['stocks']))]
        # for prod_idx,prod in enumerate(observation["products"]):
        #     initial_prods[i]['size'] = observation["products"][i]['size']
        #     initial_prods[i]['quantity'] = observation["products"][i]['quantity']
        initial_stocks = deepcopy(observation["stocks"])
        initial_prods = deepcopy(observation["products"])

        if self.policy_id == 1:
            self.furini_heuristic(initial_stocks,initial_prods)
            self.drawing_strips()
        else:
            self.lazy_init_heuristic(initial_stocks,initial_prods)
            self.drawing_patterns()

    def furini_heuristic(self, initial_stocks, initial_prods):
        # Student code here

        # print('Products: ', initial_prods)
        # stocks = []
        # for stock in initial_stocks:
        #     stock_w, stock_h = self._get_stock_size_(stock)
        #     stocks.append({'width': stock_w, 'height': stock_h})
        # print('Stocks: ', stocks)

        for prod_idx,prod in enumerate(initial_prods):
            prod_info = {'id': str(prod_idx),"width": prod["size"][0], "height": prod["size"][1], "quantity": prod["quantity"]}
            self.list_products.append(prod_info)
            # prod_num += prod["quantity"]
            prod_info = {'id': str(prod_idx) + '_rotated',"width": prod["size"][1], "height": prod["size"][0], "quantity": prod["quantity"]}
            self.list_products.append(prod_info)
        self.list_products.sort(key=lambda x: (-x['height'], -x['width']))
        # print('Start product')
        # for prod in self.list_products:
        #     print(prod)
        # print('End product')

        stock_id = 0
        for stock_i_idx,stock_i in enumerate(initial_stocks):
            stock_w, stock_h = self._get_stock_size_(stock_i)
            duplicated_stock_idx = -1
            for stock_idx,stock in enumerate(self.list_stocks):
                if min(stock_w,stock_h) == stock["width"] and max(stock_h,stock_w) == stock["length"]:
                    duplicated_stock_idx = stock_idx
                    break
            if duplicated_stock_idx != -1:
                self.list_stocks[duplicated_stock_idx]["quantity"] += 1
                self.list_stocks[duplicated_stock_idx]["stock_index"].append((stock_i_idx,stock_h > stock_w))
            else:
                stock_info = {'id': stock_id,"width": min(stock_w,stock_h), "length": max(stock_h,stock_w), "quantity": 1, "stock_index": [(stock_i_idx,stock_h > stock_w)], 'used': 0, 'rotated': stock_h > stock_w }
                stock_id += 1
                self.list_stocks.append(stock_info)
        stock_quantity = [stock['quantity'] for stock in self.list_stocks]
        self.list_stocks.sort(key=lambda x:x['width'] * x['length'])
        # print('Start stock')
        # for stock in self.list_stocks:
        #     print(stock)
        # print('End stock')

        # print('Stocks: ', self.list_stocks)

        initial_patterns = []
        bin_counter = 0
        item_demand = {item['id']: item['quantity'] for item in self.list_products}

        for item in self.list_products:
            while item_demand[item['id']] > 0:
                # bin_class_id = b_i[item['id']]
                bin_class_id = self.choose_appropriate_stock_type_for_prod(self.list_stocks,item)
                bin_class = next(bc for bc in self.list_stocks if bc['id'] == bin_class_id)
    
                # Open a new bin of this class if possible
                bin_counter += 1
                # print('bin_class: ',bin_class)
                current_bin = {'id': bin_counter, 'key': str(bin_class['id']),'bin_class_id': bin_class['id'], 'length': bin_class['length'], 'width': bin_class['width'], 'remaining_length': bin_class['length'], 'remaining_width': bin_class['width'], 'strips': []}
                initial_patterns.append(current_bin)

                while item_demand[item['id']] > 0 and current_bin['remaining_width'] >= item['height']:
                    # print(item['id'],': ',item_demand[item['id']])
                    # Initialize a new strip
                    strip_width = item['height']
                    strip_length = 0
                    strip_items = []

                    items_to_place = min(item_demand[item['id']],int(current_bin['length'] // item['width']))

                    if items_to_place == 0:
                        break  # Cannot place more items in this bin

                    # rows_needed = (items_to_place + max_items_in_row - 1) // max_items_in_row
                    strip_length = items_to_place * item['width']

                    if strip_width > current_bin['remaining_width']:
                        break  # Cannot place strip in remaining length

                    item_placement = {'item_class_id': item['id'], 'width': item['width'], 'height': item['height'],'quantity': items_to_place}
                    strip = {'length': strip_length, 'width': strip_width, 'items': [item_placement]}
                    current_bin['key'] += ''.join('_' + str(item['id']) for _ in range(items_to_place))
                    # Update bin and item demand
                    current_bin['remaining_width'] -= strip_width
                    item_demand[item['id']] -= items_to_place
                    if('_rotated' in item['id']):
                        item_demand[item['id'].replace('_rotated','')] -= items_to_place
                    else:
                        item_demand[item['id'] + '_rotated'] -= items_to_place
                    # print(item['id'],': ',item_demand[item['id']])
                    # print(item['id'].replace('_rotated',''),': ',item_demand[item['id'].replace('_rotated','')])
                    # Fill the strip with smaller items if possible (greedy procedure)
                    
                    strip_remaining_length = current_bin['length'] - strip['length']
                    if strip_remaining_length > 0:
                        for next_item in self.list_products:
                            if item_demand[next_item['id']] > 0 and next_item['width'] <= strip_remaining_length and next_item['height'] <= strip_width:
                                items_to_place = min(item_demand[next_item['id']],int(strip_remaining_length // next_item['width']))
                                if(items_to_place > 0):
                                    item_placement = {'item_class_id': next_item['id'], 'width': next_item['width'], 'height': next_item['height'],'quantity': items_to_place}
                                    current_bin['key'] += ''.join('_' + str(next_item['id']) for _ in range(items_to_place))
                                    strip['items'].append(item_placement)
                                    item_demand[next_item['id']] -= items_to_place
                                    if('_rotated' in next_item['id']):
                                        item_demand[next_item['id'].replace('_rotated','')] -= items_to_place
                                    else:
                                        item_demand[next_item['id'] + '_rotated'] -= items_to_place
                                    strip['length'] += items_to_place * next_item['width']
                                    strip_remaining_length -= items_to_place * next_item['width']
                                    if strip_remaining_length <= 0:
                                        break
                    current_bin['strips'].append(strip)
                
                while current_bin['remaining_width'] > 0:
                    canPlaceMore = False
                    for sub_item in self.list_products:
                        if item_demand[sub_item['id']] > 0 and current_bin['remaining_width'] >= sub_item['height']:
                            canPlaceMore = True

                            strip_width = sub_item['height']
                            strip_length = 0
                            strip_items = []

                            items_to_place = min(item_demand[sub_item['id']],int(current_bin['length'] // sub_item['width']))

                            if items_to_place == 0:
                                break  # Cannot place more items in this bin

                            # rows_needed = (items_to_place + max_items_in_row - 1) // max_items_in_row
                            strip_length = items_to_place * sub_item['width']

                            if strip_width > current_bin['remaining_width']:
                                break  # Cannot place strip in remaining length

                            item_placement = {'item_class_id': sub_item['id'], 'width': sub_item['width'], 'height': sub_item['height'],'quantity': items_to_place}
                            current_bin['key'] += ''.join('_' + str(sub_item['id']) for _ in range(items_to_place))

                            strip = {'length': strip_length, 'width': strip_width, 'items': [item_placement]}

                            # Update bin and item demand
                            current_bin['remaining_width'] -= strip_width
                            item_demand[sub_item['id']] -= items_to_place
                            if('_rotated' in sub_item['id']):
                                item_demand[sub_item['id'].replace('_rotated','')] -= items_to_place
                            else:
                                item_demand[sub_item['id'] + '_rotated'] -= items_to_place
                            
                            strip_remaining_length = current_bin['length'] - strip['length']
                            if strip_remaining_length > 0:
                                for next_item in self.list_products:
                                    if item_demand[next_item['id']] > 0 and next_item['width'] <= strip_remaining_length and next_item['height'] <= strip_width:
                                        items_to_place = min(item_demand[next_item['id']],int(strip_remaining_length // next_item['width']))
                                        if(items_to_place > 0):
                                            item_placement = {'item_class_id': next_item['id'],'width': next_item['width'], 'height': next_item['height'], 'quantity': items_to_place}
                                            current_bin['key'] += ''.join('_' + str(next_item['id']) for _ in range(items_to_place))
                                            strip['items'].append(item_placement)
                                            item_demand[next_item['id']] -= items_to_place
                                            if('_rotated' in next_item['id']):
                                                item_demand[next_item['id'].replace('_rotated','')] -= items_to_place
                                            else:
                                                item_demand[next_item['id'] + '_rotated'] -= items_to_place
                                            strip['length'] += items_to_place * next_item['width']
                                            strip_remaining_length -= items_to_place * next_item['width']
                                            if strip_remaining_length <= 0:
                                                break
                            current_bin['strips'].append(strip)
                    if canPlaceMore == False: break
        # print(item_demand)
        # print("Initial patterns")
        # for pattern in initial_patterns:
        #     print(pattern)
        # print("End initial")
        patterns_converted = []
        # D = np.array([])
        D = np.zeros(len(initial_prods))
        # print(self.list_products)
        # for prod in initial_prods:
        for prod in self.list_products:
            if '_rotated' in prod['id']: continue
            D[int(prod['id'])]=prod["quantity"]
        D = D.flatten()
        # print(D)

        # S = np.array([])
        S = np.zeros(len(self.list_stocks))
        for stock in self.list_stocks:
            S[int(stock['id'])] = stock['quantity']
        S = S.flatten()
        # print(S)
        
        c = np.array([])
        for pattern in initial_patterns:
            # print(pattern['key'])
            if pattern["key"] not in self.keys:
                self.keys.append(pattern["key"])
                unique_pattern = {'key': pattern['key'], "quantity": 1, "stock_type": pattern["bin_class_id"], "strips": pattern["strips"]}
                patterns_converted.append(unique_pattern)
                self.sub_optimal_patterns.append(unique_pattern)
                area = pattern['length'] * pattern['width']
                c = np.append(c,area)
            else:
                self.update_quantity_pattern_by_key(patterns_converted, pattern["key"])
        c = c.flatten()

        A = np.zeros(shape=(int(len(self.list_products) / 2),len(patterns_converted))) # 11 row - 28 col
        for pattern_idx, pattern in enumerate(patterns_converted):
            for strip in pattern['strips']:
                for item in strip['items']:
                # print(prod_index, ' ', value['quantity'])
                    if '_rotated' in item['item_class_id']: item_idx = item['item_class_id'].replace('_rotated','')
                    else: item_idx = item['item_class_id']
                    item_idx = int(item_idx)
                    # print(item_idx, ' ', pattern_idx)
                    A[item_idx][pattern_idx] += item['quantity']

        B = np.zeros(shape=(len(self.list_stocks),len(patterns_converted))) # 97 row - 28 col
        for pattern_idx, pattern in enumerate(patterns_converted):
            B[pattern["stock_type"]][pattern_idx] = 1

        # print('D: ',D)
        # print('S: ',S)
        # print('c: ',c)
        # print('A: ',A)
        # print('B: ',B)
        # print('Initial pattern: ')
        # for pattern in patterns_converted:
        #     print(pattern)
        
        x_bounds = [(0,None) for _ in range(len(patterns_converted))]
        result_simplex = linprog(c,A_ub=B,b_ub=S,A_eq=A,b_eq=D,bounds=x_bounds,method='highs')
        if(result_simplex.status == 0):
            # print(result_simplex)
            dual_prods = result_simplex.eqlin['marginals']
            dual_stocks = result_simplex.ineqlin['marginals']
            # self.list_stocks.sort(key=lambda x: x['id'])
            self.list_products.sort(key=lambda x: x['id'])
            new_patterns_generation = []
            print("Start stock")
            for stock in self.list_stocks:
                print(stock)
            print("End stock")
            # print(self.list_products)
            # print("Product: ", self.list_products)
            for i in range(len(self.list_stocks)):
                print("Finish stock ", i)
                # print("dual_prods: ",dual_prods)
                # print("Start producta")
                # for prod in self.list_products:
                #     print(prod)
                # print("End producta")
                clone_dual_prods = deepcopy(dual_prods)
                clone_dual_prods_idx = deepcopy(dual_prods)
                j = 0
                for prod in self.list_products:
                    if '_rotated' in prod['id']: continue
                    clone_dual_prods_idx[j]= int(prod['id'])
                    j+=1
                clone_dual_prods_idx = [int(x) for x in clone_dual_prods_idx]
                new_strips = self.generate_pattern(clone_dual_prods, clone_dual_prods_idx, i)
                print(new_strips)
                key = str(self.list_stocks[i]['id'])
                converted_strips = []
                for strip in new_strips:
                    items = []
                    length = 0
                    for item_count_idx,item_count in enumerate(strip['itemCount']):
                        if item_count == 0: continue
                        key += ''.join('_' + str(self.list_products[item_count_idx]['id']) for _ in range(item_count))
                        length += self.list_products[item_count_idx]['width'] * item_count
                        items.append({'item_class_id': self.list_products[item_count_idx]['id'], 'width': self.list_products[item_count_idx]['width'], 'height': self.list_products[item_count_idx]['height'], 'quantity': item_count})
                    converted_strips.append({'length': length, 'width': strip['strip'], 'items': items})
                new_patterns_generation.append({'key': key, 'quantity': 1, 'stock_type': self.list_stocks[i]['id'], 'strips': converted_strips})
            for pattern in new_patterns_generation:
                print('converted: ',pattern)

            # # Calculate reduce cost
            # solveMilp = True
            # reduce_costs = []
            # for pattern in new_patterns_generation:
            #     bin_class = next(bc for bc in self.list_stocks if bc['id'] == pattern['stock_type'])
            #     new_column_A = np.zeros(int(len(self.list_products)/2))
            #     for strip in pattern['strips']:
            #         for item in strip['items']:
            #             if '_rotated' in item['item_class_id']: item_idx = item['item_class_id'].replace('_rotated','')
            #             else: item_idx = item['item_class_id']
            #             item_idx = int(item_idx)
            #             new_column_A[item_idx] += item['quantity']
            #     reduce_cost = bin_class['width'] * bin_class['length'] - (np.dot(new_column_A,dual_prods.transpose())  + self.get_stock_price(dual_stocks,pattern['stock_type']))
            #     print(reduce_cost)
            #     if reduce_cost < 0 and pattern['key'] not in self.keys:
            #         patterns_converted.append(pattern)
            #         self.keys.append(pattern['key'])
            #         solveMilp = False
            #         c = np.append(c,bin_class['width'] * bin_class['length'])
            #         A = np.column_stack((A, new_column_A))
            #         new_column_B = np.zeros(int(len(self.list_stocks)))
            #         new_column_B[pattern["stock_type"]] = 1
            #         B = np.column_stack((B, new_column_B))
            # # print("Reduce costs: ",reduce_costs)

            # print('D after gen: ',D)
            # print('S after gen: ',S)
            # print('c after gen: ',c)
            # print(A)
            # print('B after gen: ',B)
            # if solveMilp:
            #     self.solveMilp(D,S,c,A,B,patterns_converted)
            # else:
            #     self.solveLp(D,S,c,A,B,patterns_converted,result_simplex.fun)
            # self.optimal_patterns = self.sub_optimal_patterns
            self.optimal_patterns = [
# {'key': '0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1', 'quantity': 1, 'stock_type': 0, 'strips': [{'length': np.int64(275), 'width': 14, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(25)}]}, {'length': np.int64(275), 'width': 14, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(25)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(54), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(3)}]}, {'length': np.int64(54), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(3)}]}, {'length': np.int64(54), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(3)}]}, {'length': np.int64(36), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(2)}]}, {'length': np.int64(36), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(2)}]}, {'length': np.int64(18), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(1)}]}]}
# ,{'key': '1_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1', 'quantity': 1, 'stock_type': 1, 'strips': [{'length': np.int64(275), 'width': 14, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(25)}]}, {'length': np.int64(275), 'width': 14, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(25)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(72), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(4)}]}, {'length': np.int64(54), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(3)}]}, {'length': np.int64(54), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(3)}]}, {'length': np.int64(54), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(3)}]}, {'length': np.int64(36), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(2)}]}, {'length': np.int64(36), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(2)}]}, {'length': np.int64(18), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(1)}]}]}
# ,{'key': '2_1_1_1_1_1_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_2_2_2_2_2', 'quantity': 1, 'stock_type': 2, 'strips': [{'length': np.int64(90), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(5)}]}, {'length': np.int64(440), 'width': 14, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(40)}]}, {'length': np.int64(250), 'width': 39, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(5)}, {'item_class_id': '2', 'width': np.int64(39), 'height': np.int64(14), 'quantity': np.int64(5)}]}]}
# ,{'key': '4_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_2_2_2_2_2', 'quantity': 1, 'stock_type': 4, 'strips': [{'length': np.int64(90), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(5)}]}, {'length': np.int64(90), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(5)}]}, {'length': np.int64(90), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(5)}]}, {'length': np.int64(90), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(5)}]}, {'length': np.int64(396), 'width': 14, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(36)}]}, {'length': np.int64(195), 'width': 39, 'items': [{'item_class_id': '2', 'width': np.int64(39), 'height': np.int64(14), 'quantity': np.int64(5)}]}]}
# ,{'key': '3_0_rotated_0_rotated_0_rotated_0_rotated_1_1_1_1_1_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_0_2_2_2_2_2', 'quantity': 1, 'stock_type': 3, 'strips': [{'length': np.int64(56), 'width': 11, 'items': [{'item_class_id': '0_rotated', 'width': np.int64(14), 'height': np.int64(11), 'quantity': np.int64(4)}]}, {'length': np.int64(90), 'width': 2, 'items': [{'item_class_id': '1', 'width': np.int64(18), 'height': np.int64(2), 'quantity': np.int64(5)}]}, {'length': np.int64(429), 'width': 14, 'items': [{'item_class_id': '0', 'width': np.int64(11), 'height': np.int64(14), 'quantity': np.int64(39)}]}, {'length': np.int64(195), 'width': 39, 'items': [{'item_class_id': '2', 'width': np.int64(39), 'height': np.int64(14), 'quantity': np.int64(5)}]}]}             
            ]
        else:
            self.optimal_patterns = self.sub_optimal_patterns
            # for pattern in self.optimal_patterns:
            #     print(pattern)

    def get_stock_price(self,dual_stocks,stock_type):
        for stock_idx, stock in enumerate(self.list_stocks):
            if stock['id'] == stock_type:
                return dual_stocks[stock_idx]

    def lazy_init_heuristic(self,initial_stocks,initial_prods):
        prod_num = 0
        for prod_idx,prod in enumerate(initial_prods):
            prod_info = {"width": prod["size"][0], "height": prod["size"][1], "quantity": prod["quantity"]}
            self.list_products.append(prod_info)
            prod_num += prod["quantity"]

        for stock_i_idx,stock_i in enumerate(initial_stocks):
            stock_w, stock_h = self._get_stock_size_(stock_i)
            duplicated_stock_idx = -1
            for stock_idx,stock in enumerate(self.list_stocks):
                if stock_w == stock["width"] and stock_h == stock["height"]:
                    duplicated_stock_idx = stock_idx
                    break
            if duplicated_stock_idx != -1:
                self.list_stocks[duplicated_stock_idx]["quantity"] += 1
                self.list_stocks[duplicated_stock_idx]["stock_index"].append(stock_i_idx)
            else:
                stock_info = {"width": stock_w, "height": stock_h, "quantity": 1, "stock_index": [stock_i_idx]}
                self.list_stocks.append(stock_info)

        # Pattern for all stocks
        # pattern = {'stock_idx': number, 'items': map[]}[]
        # map: (key-value) -> (prod_idx: {"quantity": number, "positions": number[][], "width": number, "height": number})
        
        # Initialize the pattern
        initial_patterns = []
        for stock_idx, stock in enumerate(initial_stocks):
            stock_w, stock_h = self._get_stock_size_(stock)
            stock_type = -1
            for s_idx,s in enumerate(self.list_stocks):
                if s["width"] == stock_w and s["height"] == stock_h:
                    stock_type = s_idx
                    break
            pattern_element = {'key': '_' + str(stock_type) + '_','stock_idx': stock_idx, 'stock_type': stock_type, 'width': stock_w,'height': stock_h,'items': {}}
            initial_patterns.append(pattern_element)

        clone_stocks = initial_stocks
        clone_prods = initial_prods
        if len(self.indices_prods) == 0:
            self.indices_prods = list(range(len(clone_prods)))
        for _ in range(prod_num):
            heuristic_result = self.lazy_init(clone_prods, clone_stocks, self.indices_prods)
            prod_idx = heuristic_result["prod_idx"]
            best_stock_idx = heuristic_result["stock_idx"]
            best_position = heuristic_result["position"]
            best_prod_size = heuristic_result["size"]
            # print("prod_idx: ", prod_idx, "best_stock_idx: ", best_stock_idx, "position: ", best_position, "prod_size: ", best_prod_size)
            clone_stocks, clone_prods = self.fill_to_clone_stocks(clone_stocks, clone_prods, prod_idx, best_stock_idx, best_position, best_prod_size)
            if prod_idx in initial_patterns[best_stock_idx]["items"]:
                initial_patterns[best_stock_idx]["items"][prod_idx]["quantity"] += 1
                initial_patterns[best_stock_idx]["items"][prod_idx]["positions"].append(best_position)
                initial_patterns[best_stock_idx]["key"]+=str(prod_idx) + '_'
            else:
                position_list = [best_position]
                prod_w, prod_h = best_prod_size
                initial_patterns[best_stock_idx]["items"][prod_idx] = {"quantity": 1, "positions": position_list, "width": prod_w, "height": prod_h }
                initial_patterns[best_stock_idx]["key"]+=str(prod_idx) + '_'
        
        patterns_converted = []
        for pattern in initial_patterns:
            if pattern["items"] == {}: continue   
            if pattern["key"] not in self.keys:
                self.keys.append(pattern["key"])
                unique_pattern = {"key": pattern['key'], "quantity": 1, "stock_type": pattern["stock_type"], "items": pattern["items"]}
                patterns_converted.append(unique_pattern)
            else:
                self.update_quantity_pattern_by_key(patterns_converted,pattern['key'])
        self.optimal_patterns = patterns_converted
            
    def fill_to_clone_stocks(self,clone_stocks, clone_prods, prod_idx, best_stock_idx, best_position, best_prod_size):
        x, y = best_position
        w, h = best_prod_size
        for i in range(x, x + w):
            for j in range(y, y + h):
                clone_stocks[best_stock_idx][i][j] = prod_idx
        return clone_stocks, clone_prods

    def lazy_init(self, clone_prods, clone_stocks, indices_prods):
        best_stock_idx, best_position, best_prod_size = -1, None, [0, 0]
        if self.sorted_prods == []:
            self.sorted_prods = sorted(clone_prods, key=lambda p: p["size"][0] * p["size"][1], reverse=True)
            self.indices_prods = sorted(self.indices_prods, key=lambda i: clone_prods[i]["size"][0] * clone_prods[i]["size"][1], reverse=True)
            # self.sorted_prods = sorted(self.list_products, key=lambda p: (p["size"][0], p["size"][1]), reverse=True)
        # if not hasattr(self, 'sorted_stocks'):
        #     self.sorted_stocks = sorted(enumerate(clone_stocks), key=lambda x: self._get_stock_size_(x[1])[0] * self._get_stock_size_(x[1])[1])

        clone_prods = self.sorted_prods
        # sorted_stocks = self.sorted_stocks
        # print("Sorted first stock: ",self._get_stock_size_(sorted_stocks[0][1]))
        # Group stocks into buckets based on size ranges
        self._group_stocks_into_buckets(clone_stocks)
        # print(clone_prods)
        
        for prod_idx,prod in enumerate(clone_prods):
            if prod["quantity"] > 0:
                prod_size = prod["size"]
                min_waste_percentage = float('inf')
                candidate_stocks = self._get_candidate_stocks(prod_size)
                
                for stock_idx, stock in candidate_stocks:
                    placed = False
                    position = self._find_position(stock, prod_size[0], prod_size[1])
                    if position:
                        stock_w, stock_h = self._get_stock_size_(stock)
                        stock_area = stock_w * stock_h
                        prod_area = prod_size[0] * prod_size[1]
                        waste_percentage = (stock_area - prod_area) / stock_area
                        if waste_percentage < min_waste_percentage:
                            min_waste_percentage = waste_percentage
                            best_stock_idx = stock_idx
                            best_position = position
                            best_prod_size = prod_size
                            placed = True
                            break
                if best_position and best_stock_idx != -1:
                    prod["quantity"] -= 1
                    return {"prod_idx": self.indices_prods[prod_idx], "stock_idx": best_stock_idx, "size": (best_prod_size[0], best_prod_size[1]), "position": best_position}
        return {"stock_idx": -1, "size": [0, 0], "position": None}

    def _group_stocks_into_buckets(self, stocks):
        self.stock_buckets = {}
        for idx, stock in enumerate(stocks):
            stock_w, stock_h = self._get_stock_size_(stock)
            bucket_key = (stock_w // self.bucket_size, stock_h // self.bucket_size)
            if bucket_key not in self.stock_buckets:
                self.stock_buckets[bucket_key] = []
            self.stock_buckets[bucket_key].append((idx, stock))

    def _get_candidate_stocks(self, prod_size):
        prod_w, prod_h = prod_size
        bucket_key = (prod_w // self.bucket_size, prod_h // self.bucket_size)
        candidate_stocks = []
        for key in self.stock_buckets:
            if key[0] >= bucket_key[0] and key[1] >= bucket_key[1]:
                candidate_stocks.extend(self.stock_buckets[key])
        return candidate_stocks

    def _find_position(self, stock, product_width, product_height):
        stock_width, stock_height = self._get_stock_size_(stock)

        for x in range(stock_width - product_width + 1):
            for y in range(stock_height - product_height + 1):
                if self._can_place_(stock, (x, y), (product_width, product_height)):
                    return (x, y)
        return None

    #########################################################################

    def solveLp(self,D,S,c,A,B,patterns_converted,result):
        print('Cache result: ', result)
        x_bounds = [(0,None) for _ in range(len(patterns_converted))]        
        result_simplex = linprog(c,A_ub=B,b_ub=S,A_eq=A,b_eq=D,bounds=x_bounds,method='highs')
        if(result_simplex.status == 0):
            print(result_simplex)
            dual_prods = result_simplex.eqlin['marginals']
            dual_stocks = result_simplex.ineqlin['marginals']
            new_patterns_generation = []
            # print(self.list_products)
            # self.list_products.sort(key=lambda x: x['id'])
            # print("Product: ", self.list_products)
            for i in range(len(self.list_stocks)):
                print("Finish stock ", i)
                new_strips = self.generate_pattern(dual_prods, i)
                # print(new_strips)
                key = str(self.list_stocks[i]['id'])
                converted_strips = []
                for strip in new_strips:
                    items = []
                    length = 0
                    for item_count_idx,item_count in enumerate(strip['itemCount']):
                        if item_count == 0: continue
                        key += ''.join('_' + str(self.list_products[item_count_idx]['id']) for _ in range(item_count))
                        length += self.list_products[item_count_idx]['width'] * item_count
                        items.append({'item_class_id': self.list_products[item_count_idx]['id'], 'width': self.list_products[item_count_idx]['width'], 'height': self.list_products[item_count_idx]['height'], 'quantity': item_count})
                    converted_strips.append({'length': length, 'width': strip['strip'], 'items': items})
                new_patterns_generation.append({'key': key, 'quantity': 1, 'stock_type': self.list_stocks[i]['id'], 'strips': converted_strips})

            # for pattern in new_patterns_generation:
            #     print('converted: ',pattern)
            # for i in range(len(self.list_stocks)):
            #     strips = self.generate_pattern(dual_prods, i)
            #     key = str(self.list_stocks[i]['id'])
            #     converted_strips = []
                # for strip in strips:
                #     items = []
                #     length = 0
                #     for item_count_idx,item_count in enumerate(strip['itemCount']):
                #         if item_count == 0: continue
                #         key += ''.join('_' + str(self.list_products[item_count_idx]['id']) for _ in range(item_count))
                #         length += self.list_products[item_count_idx]['width'] * item_count
                #         items.append({'item_class_id': self.list_products[item_count_idx]['id'], 'width': self.list_products[item_count_idx]['width'], 'height': self.list_products[item_count_idx]['height'], 'quantity': item_count})
                #     converted_strips.append({'length': length, 'width': strip['strip'], 'items': items})
                # new_patterns_generation.append({'key': key, 'quantity': 1, 'stock_type': self.list_stocks[i]['id'], 'strips': converted_strips})
                # for pattern in new_patterns_generation:
                #     print('converted: ',pattern)

            # Calculate reduce cost
            solveMilp = True
            reduce_costs = []
            for pattern in new_patterns_generation:
                bin_class = next(bc for bc in self.list_stocks if bc['id'] == pattern['stock_type'])
                new_column_A = np.zeros(int(len(self.list_products)/2))
                for strip in pattern['strips']:
                    for item in strip['items']:
                        if '_rotated' in item['item_class_id']: item_idx = item['item_class_id'].replace('_rotated','')
                        else: item_idx = item['item_class_id']
                        item_idx = int(item_idx)
                        new_column_A[item_idx] += item['quantity']
                reduce_cost = bin_class['width'] * bin_class['length'] - (np.dot(new_column_A,dual_prods.transpose())  + self.get_stock_price(dual_stocks,pattern['stock_type']))
                print(reduce_cost)
                if reduce_cost < 0 and pattern['key'] not in self.keys:
                    patterns_converted.append(pattern)
                    self.keys.append(pattern['key'])
                    solveMilp = False
                    c = np.append(c,bin_class['width'] * bin_class['length'])
                    A = np.column_stack((A, new_column_A))
                    new_column_B = np.zeros(int(len(self.list_stocks)))
                    new_column_B[pattern["stock_type"]] = 1
                    B = np.column_stack((B, new_column_B))
            # print("Reduce costs: ",reduce_costs)

            print('D after gen: ',D)
            print('S after gen: ',S)
            print('c after gen: ',c)
            print(A)
            print('B after gen: ',B)
            if solveMilp:
                self.solveMilp(D,S,c,A,B,patterns_converted)
            else:
                self.solveLp(D,S,c,A,B,patterns_converted,result_simplex.fun)
        else:
            self.optimal_patterns = self.sub_optimal_patterns
            # for pattern in self.optimal_patterns:
            #     print(pattern)

    def solveMilp(self,D,S,c,A,B,patterns_converted):
        print('D Milp: ',D)
        print('S Milp: ',S)
        print('c Milp: ',c)
        print('A Milp: ',A)
        print('B Milp: ',B)
        x_bounds = [(0,None) for _ in range(len(c))]
        optimal_result = linprog(c,A_ub=B,b_ub=S,A_eq=A,b_eq=D,bounds=x_bounds,method='highs',integrality=1)
        print("Optimal Result")
        print(optimal_result)
        if optimal_result.status == 0:
            patterns_quantity = np.int_(optimal_result.x)
            total_area = 0
            for pattern_idx,pattern in enumerate(patterns_converted):
                pattern['quantity'] = patterns_quantity[pattern_idx]
                if pattern['quantity'] != 0: total_area += self.list_stocks[pattern['stock_type']]['length'] * self.list_stocks[pattern['stock_type']]['width'] * pattern['quantity']
            # for pattern in patterns_converted:
            #     print(pattern)
            print('Total area', total_area)
            self.optimal_patterns = patterns_converted
        else:
            self.optimal_patterns = self.sub_optimal_patterns

    def choose_appropriate_stock_type_for_prod(self,list_stocks,item):
        max_items_in_bin = 0
        assigned_bin_class = None
        for bin_class in list_stocks:
            if bin_class['used'] < bin_class['quantity']:
                max_items = int((bin_class['width'] // item['height']) * (bin_class['length'] // item['width']))
                if max_items >= item['quantity']:
                    assigned_bin_class = bin_class
                    break
                elif max_items > max_items_in_bin:
                    max_items_in_bin = max_items
                    assigned_bin_class = bin_class
        if assigned_bin_class:
            # b_i[item['id']] = assigned_bin_class['id']
            assigned_bin_class['used'] += 1
            return assigned_bin_class['id']
        else:
            raise Exception(f"No available bin can accommodate item class {item['id']}")

    def get_stock_by_type(self,stock_type):
        for stock in self.list_stocks:
            if stock['id'] == stock_type:
                return stock

    def drawing_strips(self):
        # print("Final patterns")
        for data in self.optimal_patterns:
            if data['quantity'] == 0: continue
            # print(data)                
            for _ in range(data['quantity']):
                stock = self.get_stock_by_type(data['stock_type'])
                stock_idx_info = stock['stock_index'][0]
                stock['stock_index'].pop(0)
                x,y = 0,0
                for strip in data['strips']:
                    if stock_idx_info[1]:
                        for item in strip['items']:
                            for _ in range(item['quantity']):
                                size = (item['height'],item['width'])
                                position = (x,y)
                                y += item['width']
                                self.drawing_data.append({
                                    'stock_idx': stock_idx_info[0],
                                    'size': size,
                                    'position': position,
                                })
                        x += strip['width']
                        y = 0
                    else:
                        for item in strip['items']:
                            for _ in range (item['quantity']):
                                size = (item['width'],item['height'])
                                position = (x,y)
                                x += item['width']
                                self.drawing_data.append({
                                    'stock_idx': stock_idx_info[0],
                                    'size': size,
                                    'position': position,
                                })
                        y += strip['width']
                        x = 0
            
            # print(stock)
            # stock_idx, rotated = self.get_stock_idx_to_draw(stock_type)

    def drawing_patterns(self):
        for data in self.optimal_patterns:
            if data['quantity'] == 0: continue
            for _ in range(data['quantity']):
                stock_type = data['stock_type']
                stock_idx = self.list_stocks[stock_type]['stock_index'][0]
                self.list_stocks[stock_type]['stock_index'].pop(0)
                items = data['items']
                if items:
                    for item_id, details in items.items():
                        size = (details['width'], details['height'])
                        positions = details['positions']
                        for position in positions:
                            self.drawing_data.append({
                                'stock_idx': stock_idx,
                                'size': size,
                                'position': position,
                            })
    
    def update_quantity_pattern_by_key(self,patterns_converted,key):
        for pattern in patterns_converted:
            if(pattern['key'] == key):
                pattern['quantity'] += 1
                break

    def generate_pattern(self, dual_prods, dual_prods_idx, stock_type):
        #Initialize
        top = 6
        result = []
        # print(list_stocks)
        # list_stocks.sort(key=lambda x: x['id'])
        # if(self.list_stocks[stock_type]['rotated']):
        clone_dual_prods = deepcopy(dual_prods)
        # for i in range(len(clone_dual_prods)):
        #     dual_prods[dual_prods_idx[i]] = clone_dual_prods[i]
        stock_w = self.list_stocks[stock_type]['length']
        stock_h = self.list_stocks[stock_type]['width']
        # else:
        #     stock_w = self.list_stocks[stock_type]['width']
        #     stock_h = self.list_stocks[stock_type]['length']
        clone_products = deepcopy(self.list_products)
        for prod in clone_products:
            if '_rotated' in prod['id']:
                prod['id'] = int(prod['id'].replace('_rotated', '')) * 2 + 1
            else:
                prod['id'] = int(prod['id']) * 2
        clone_products.sort(key=lambda x: x['id'])
        product_widths = np.array([prod['height'] for prod in clone_products])
        product_heights = np.array([prod['width'] for prod in clone_products])
        # cut horizontal strips
        for i in range(len(product_heights)):
            if product_widths[i] > stock_w or product_heights[i] > stock_h:
                continue
            profit = np.zeros(stock_w + 1)
            itemCount = np.zeros(len(self.list_products))
            for j in range(len(product_widths)):
                if product_heights[j] > product_heights[i] or product_widths[j] > stock_w:
                    continue
                itemCount[j] = stock_w // product_widths[j]
            result.append({"strip": int(product_heights[i]), "profit": int(profit[stock_w]), "itemCount": itemCount.astype(int)})
        result = np.array(result)
        # print("Result: ", result)
        small_result = []
        prod_clone = deepcopy(self.list_products)
        print("Start product")
        for prod in prod_clone:
            if '_rotated' in prod['id']:
                prod['id'] = int(prod['id'].replace('_rotated', '')) * 2 + 1
            else:
                prod['id'] = int(prod['id']) * 2
        prod_clone.sort(key=lambda x: x['id'], reverse=False)
        top_strips = np.zeros((top * len(product_heights), 1), dtype = int)
        for strips in result:
            strips['profit'] = int(strips['profit'])
            strips['strip'] = int(strips['strip'])
            existing_patterns = set()
            for i in range(len(strips["itemCount"])):

                array_cal = np.zeros(len(strips["itemCount"]), dtype=int)
                array_cal[i] = int(strips["itemCount"][i])

                if prod_clone[i]["height"] > strips["strip"]:
                    continue

                small_profit = array_cal[i] * dual_prods[int(prod_clone[i]['id'] / 2)]
                small_l = product_widths[i] * array_cal[i]

                # Add initial pattern
                pattern_key = tuple(array_cal)
                if pattern_key not in existing_patterns:
                    small_result.append({
                        "strip": int(strips["strip"]),
                        "profit": int(small_profit),
                        "itemCount": array_cal.copy()
                    })
                    existing_patterns.add(pattern_key)
                clone_array_cal = array_cal.copy()
                clone_small_profit = small_profit
                prod_clone_clone = deepcopy(prod_clone)
                for k in range(array_cal[i]-1, 0, -1):
                    clone_array_cal[i] = k
                    small_result.append({
                        "strip": int(strips["strip"]),
                        "profit": int(small_profit - dual_prods[int(prod_clone[i]['id'] / 2)] * (array_cal[i] - k)),
                        "itemCount": clone_array_cal.copy()
                    })
                if small_l >= stock_w:
                    continue
                prod_clone.sort(key=lambda x: dual_prods[int(x['id'] / 2)], reverse=False)
                for j in range(len(prod_clone)):
                    if prod_clone[j]["height"] > strips["strip"] or prod_clone[j]["width"] > stock_w - small_l:
                        continue
                    if prod_clone[j]["id"] == prod_clone[i]['id']:
                        continue
                    max_k = min(prod_clone[j]["quantity"], int((stock_w - small_l) // product_widths[j]))
                    for k in range(max_k, 0, -1):
                        array_cal[prod_clone[j]["id"]] += 1
                        small_profit += dual_prods[int(prod_clone[j]["id"] / 2)]
                        small_l += product_widths[j]

                        pattern_key = tuple(array_cal)
                        if pattern_key not in existing_patterns:
                            small_result.append({
                                "strip": int(strips["strip"]),
                                "profit": int(small_profit),
                                "itemCount": array_cal.copy()
                            })
                            existing_patterns.add(pattern_key)

                            if small_l >= stock_w:
                                break

                    # Reset for next iteration
                    small_profit -= dual_prods[int(prod_clone[j]["id"] / 2)] * max_k
                    small_l -= product_widths[j] * max_k
                    array_cal[prod_clone[j]["id"]] -= max_k
                prod_clone = deepcopy(prod_clone_clone)
        prod_heights = [prod['height'] for prod in self.list_products]
        small_result.sort(key=lambda x: (x["strip"], -x["profit"]))
        h_strips = np.zeros((top * len(product_heights), 1), dtype = int)
        h_stock = np.zeros((top * len(product_heights), 1), dtype = int)
        min_array = np.zeros((top * len(product_heights), 1), dtype = int)
        strip_list = []
        strip_idx = [strip['strip'] for strip in small_result]
        for i in range(len(prod_heights)):
            current_strips = [s for s in small_result if s['strip'] == prod_heights[i]]
            seen_patterns = set()
            unique_strips = []
            for strip in current_strips:
                key = (strip['strip'], tuple(strip['itemCount']))
                if key not in seen_patterns:
                    seen_patterns.add(key)
                    unique_strips.append(strip)
            current_strips = unique_strips
            current_strips.sort(key=lambda x: -x['profit'])
            # if len(current_strips) < top:
            #     for i in range(len(prod_clone)):
            #         for j in range(top):
            #             h_strips[i*top+j][0] = prod_heights[i]
            #             h_stock[i*top+j][0] = stock_h
            #     for strip in current_strips:
            #         min_for_array = 1000000
            #         min2 = 1000000
            #         for j in range(len(strip['itemCount'])):
            #             d_i = min(int(self.list_products[j]['quantity']), int(stock_h * stock_w / (product_widths[j] * product_heights[j])))
            #             min2 = min(d_i / strip['itemCount'][j], min2)
            #         min_for_array = min(min2, stock_h / strip['strip'])
            #         min_array[i*top][0] = int(min_for_array)
            #         top_strips[i*top][0] = strip['profit']
            # else:
            count = 0
            for k in range(len(h_stock)):
                h_stock[k][0] = stock_h
            for strip in current_strips[:top]:
                min_for_array = 1000000
                min2 = 1000000
                for j in range(len(strip['itemCount'])):
                    if strip['itemCount'][j] == 0: continue
                    d_i = min(int(self.list_products[j]['quantity']), int(stock_h * stock_w / (product_widths[j] * product_heights[j])))
                    min2 = min(d_i, min2, strip['itemCount'][j])
                min_for_array = min(min2, stock_h // strip['strip'])
                min_array[i*top+count][0] = min_for_array
                top_strips[i*top+count][0] = strip['profit']
                h_strips[i*top+count][0] = strip['strip']
                strip_list.append(strip)
                count += 1
            if (len(current_strips) < top):
                for _ in range (top - len(current_strips)):
                    strip_list.append({"strip": 0, "profit": 0, "itemCount": np.zeros(len(product_heights),dtype=int)})
        # print('top_strips: ', top_strips.transpose())
        # print('h_strips: ', h_strips.transpose())
        # print('h_stock: ', h_stock.transpose())
        # print('min_array: ', min_array.transpose())

        prod_demand_constraints = np.array([])
        for product in clone_products:
            if product['id'] % 2 == 1: continue
            prod_demand_constraints = np.append(prod_demand_constraints,product['quantity'])
        # print('demand: ',prod_demand_constraints)

        prod_quantity_in_strip = np.zeros((int(len(clone_products)/2),len(top_strips)))
        for i in range(int(len(clone_products)/2)):
            for j in range(len(top_strips)):
                prod_quantity_in_strip[i][j] = strip_list[j]['itemCount'][i * 2] + strip_list[j]['itemCount'][i * 2 + 1]
        # print('prod_quantity_in_strip: ',prod_quantity_in_strip)

        A = np.array([h_strips.transpose()]).reshape(-1, h_strips.shape[0])
        for i in range(0,len(min_array)):
            constraint_binary = np.zeros(len(min_array))
            constraint_binary[i] = 1
            A = np.vstack((A,constraint_binary))
        for quantity_strip in prod_quantity_in_strip:
            A = np.vstack((A,quantity_strip))

        b_u = np.array([stock_h])
        for min_array_element in min_array.transpose():
            b_u = np.append(b_u,min_array_element)
        for demand_constraint in prod_demand_constraints:
            b_u = np.append(b_u,demand_constraint)

        b_l = np.full_like(b_u,-np.inf,dtype=float)
        constraints = LinearConstraint(A,b_l,b_u)
        integrality = np.ones_like(len(top_strips))

        # B1 * (số product thứ 1 (normal + rotated) + số product thứ 2 (normal + rotated)) + B2 * (số product thứ 1 + số product thứ 2 + ... số product thứ n) + ... = Ma trận demand
        # print(clone_products)
        # print(clone_products)
        # 2 2
        # 2 2
        # print(len(strip_list))

        res = milp(c=-top_strips.transpose().reshape(-1), constraints=constraints, integrality=integrality)
        print(res)
        return_res = []
        print("res.x: ", res.x)
        for i in range(len(res.x)):
            if res.x[i] != 0:
                for j in range(int(res.x[i])):
                    return_res.append(strip_list[i])
        # print('return_res: ',return_res)
        return tuple(return_res)