from policy import Policy
import numpy as np
from scipy.optimize import linprog
import time
import copy

class Policy2210xxx(Policy):
    # def __init__(self):
    #     self.stock_buckets = {}
    #     self.bucket_size = 10  # Define the size range for each bucket
    #     self.optimal_patterns = []
    #     self.isComputing = True
    #     self.drawing_counter = -1
    #     self.drawing_data = []
    #     self.indices_prods = []
    #     self.list_stocks = []
    #     self.list_products = []

    # def get_action(self, observation, info):
    #     if(self.isComputing):
    #         self.solve_cutting_stock_problem(observation,info)
    #         self.isComputing = False
    #         for data in self.optimal_patterns:
    #             if data['quantity'] == 0: continue
    #             for _ in range(data['quantity']):
    #                 stock_type = data['stock_type']
    #                 stock_idx = self.list_stocks[stock_type]['stock_index'][0]
    #                 self.list_stocks[stock_type]['stock_index'].pop(0)
    #                 items = data['items']
    #                 if items:
    #                     for item_id, details in items.items():
    #                         size = (details['width'], details['height'])
    #                         positions = details['positions']
    #                         for position in positions:
    #                             self.drawing_data.append({
    #                                 'stock_idx': stock_idx,
    #                                 'size': size,
    #                                 'position': position,
    #                             })
    #         self.drawing_counter += 1
    #         return {
    #             "stock_idx": self.drawing_data[self.drawing_counter]["stock_idx"],
    #             "size": self.drawing_data[self.drawing_counter]["size"],
    #             "position": self.drawing_data[self.drawing_counter]["position"]
    #         }
    #     else:
    #         self.drawing_counter += 1
    #         return {
    #             "stock_idx": self.drawing_data[self.drawing_counter]["stock_idx"],
    #             "size": self.drawing_data[self.drawing_counter]["size"],
    #             "position": self.drawing_data[self.drawing_counter]["position"]
    #         }

    # def solve_cutting_stock_problem(self, observation, info):
    #     initial_stocks = copy.deepcopy(observation["stocks"])
    #     initial_prods = copy.deepcopy(observation["products"])
    #     prod_num = 0
    #     for prod_idx,prod in enumerate(initial_prods):
    #         prod_info = {"width": prod["size"][0], "height": prod["size"][1], "quantity": prod["quantity"]}
    #         self.list_products.append(prod_info)
    #         prod_num += prod["quantity"]

    #     for stock_i_idx,stock_i in enumerate(initial_stocks):
    #         stock_w, stock_h = self._get_stock_size_(stock_i)
    #         duplicated_stock_idx = -1
    #         for stock_idx,stock in enumerate(self.list_stocks):
    #             if stock_w == stock["width"] and stock_h == stock["height"]:
    #                 duplicated_stock_idx = stock_idx
    #                 break
    #         if duplicated_stock_idx != -1:
    #             self.list_stocks[duplicated_stock_idx]["quantity"] += 1
    #             self.list_stocks[duplicated_stock_idx]["stock_index"].append(stock_i_idx)
    #         else:
    #             stock_info = {"width": stock_w, "height": stock_h, "quantity": 1, "stock_index": [stock_i_idx]}
    #             self.list_stocks.append(stock_info)

    #     # Pattern for all stocks
    #     # pattern = {'stock_idx': number, 'items': map[]}[]
    #     # map: (key-value) -> (prod_idx: {"quantity": number, "positions": number[][], "width": number, "height": number})
        
    #     # Initialize the pattern
    #     initial_patterns = []
    #     for stock_idx, stock in enumerate(initial_stocks):
    #         stock_w, stock_h = self._get_stock_size_(stock)
    #         stock_type = -1
    #         for s_idx,s in enumerate(self.list_stocks):
    #             if s["width"] == stock_w and s["height"] == stock_h:
    #                 stock_type = s_idx
    #                 break
    #         pattern_element = {'key': '_' + str(stock_type) + '_','stock_idx': stock_idx, 'stock_type': stock_type, 'width': stock_w,'height': stock_h,'items': {}}
    #         initial_patterns.append(pattern_element)

    #     clone_stocks = initial_stocks
    #     clone_prods = initial_prods
    #     if len(self.indices_prods) == 0:
    #         self.indices_prods = list(range(len(clone_prods)))
    #     for _ in range(prod_num):
    #         heuristic_result = self.lazy_init_heuristic(clone_prods, clone_stocks, self.indices_prods)
    #         prod_idx = heuristic_result["prod_idx"]
    #         best_stock_idx = heuristic_result["stock_idx"]
    #         best_position = heuristic_result["position"]
    #         best_prod_size = heuristic_result["size"]
    #         # print("prod_idx: ", prod_idx, "best_stock_idx: ", best_stock_idx, "position: ", best_position, "prod_size: ", best_prod_size)
    #         clone_stocks, clone_prods = self.fill_to_clone_stocks(clone_stocks, clone_prods, prod_idx, best_stock_idx, best_position, best_prod_size)
    #         if prod_idx in initial_patterns[best_stock_idx]["items"]:
    #             initial_patterns[best_stock_idx]["items"][prod_idx]["quantity"] += 1
    #             initial_patterns[best_stock_idx]["items"][prod_idx]["positions"].append(best_position)
    #             initial_patterns[best_stock_idx]["key"]+=str(prod_idx) + '_'
    #         else:
    #             position_list = [best_position]
    #             prod_w, prod_h = best_prod_size
    #             initial_patterns[best_stock_idx]["items"][prod_idx] = {"quantity": 1, "positions": position_list, "width": prod_w, "height": prod_h }
    #             initial_patterns[best_stock_idx]["key"]+=str(prod_idx) + '_'
        
    #     # Simplex method init
    #     D = np.array([])
    #     for prod in self.list_products:
    #         D=np.append(D,prod["quantity"])
    #     D = D.flatten()
    #     # print('D: ',D)

    #     S = np.array([])
    #     for stock in self.list_stocks:
    #         S=np.append(S,stock["quantity"])
    #     S = S.flatten()
    #     # print('S: ',S)

    #     # self.initial_patterns.append({'key': '_83_0_', 'stock_idx': 84, 'stock_type': 83, 'width': np.int64(51), 'height': np.int64(50), 'items': {0: {'quantity': 1, 'positions': [(0, 0)], 'width': np.int64(41), 'height': np.int64(45)}}})
    #     keys = []
    #     c = np.array([])
    #     for pattern in initial_patterns:
    #         if pattern["items"] == {}: continue   
    #         if pattern["key"] not in keys:
    #             keys.append(pattern["key"])
    #             unique_pattern = {"quantity": 0, "stock_type": pattern["stock_type"], "items": pattern["items"]}
    #             self.optimal_patterns.append(unique_pattern)
    #             area = pattern['width'] * pattern['height']
    #             # print(unique_pattern)
    #             c = np.append(c,area)
    #     c = c.flatten()
    #     # print('c: ', c)
     
    #     A = np.zeros(shape=(len(self.list_products),len(self.optimal_patterns))) # 11 row - 28 col
    #     for pattern_idx, pattern in enumerate(self.optimal_patterns):
    #         for prod_idx, value in pattern['items'].items():
    #             # print(prod_index, ' ', value['quantity'])
    #             A[prod_idx][pattern_idx] = value['quantity']
    #     # print('A: ', A)

    #     B = np.zeros(shape=(len(self.list_stocks),len(self.optimal_patterns))) # 97 row - 28 col
    #     for pattern_idx, pattern in enumerate(self.optimal_patterns):
    #         B[pattern["stock_type"]][pattern_idx] = 1
    #     # print('B: ', B)

    #     #### Simplex method
    #     # print((np.concatenate((A,B),axis=0)).shape)

    #     x_bounds = [(0,None) for _ in range(len(self.optimal_patterns))]
    #     result_simplex = linprog(c,A_ub=B,b_ub=S,A_eq=A,b_eq=D,bounds=x_bounds,method='highs',integrality=1)
    #     x = result_simplex.x
    #     x = np.int64(x)
    #     # print(x)
    #     dual_prods = result_simplex.eqlin['marginals']
    #     dual_stocks = result_simplex.ineqlin['marginals']
    #     for i in range(len(x)):
    #         self.optimal_patterns[i]['quantity'] = x[i]
    #         # self.optimal_patterns[i]['quantity'] = 1

    #     # 2 vector Dual_variable (về item + về loại stock) 
    #     # Mỗi loại stock, truyền vô cái Long làm 
    #     # => Trả về [số loại stock] pattern + profit tương ứng
    #     # Cầm đống pattern mới kiếm tính reduce cost
    #     reduce_costs = []
    #     for pattern_idx,pattern in enumerate(self.optimal_patterns):            
    #         # print(np.dot(A[:,pattern_idx],dual_prods.transpose()))
    #         reduce_cost = c[pattern_idx] - (np.dot(A[:,pattern_idx],dual_prods.transpose())  + dual_stocks[pattern['stock_type']])
    #         reduce_costs.append(reduce_cost)

    # #     for i in range (len(reduce_costs)):
    # #         if reduce_costs[i] < 0:
    # #             # Bo vo RMP
    # #             # Giai lai simplex
    # #             print(reduce_costs[i])
        
    # #     # result_simplex_milp = linprog(c,A_ub=B,b_ub=S,A_eq=A,b_eq=D,bounds=x_bounds,method='highs', integrality=1)
    # #     # print(reduce_costs)
    # #     # Âm -> Có pattern mới vào RMP -> Quay lại step 1
    # #     # Dương -> Giải MILP để cho ra kết quả nguyên -> Siuuuuuuuuuuuuuu
    
    # def fill_to_clone_stocks(self,clone_stocks, clone_prods, prod_idx, best_stock_idx, best_position, best_prod_size):
    #     x, y = best_position
    #     w, h = best_prod_size
    #     for i in range(x, x + w):
    #         for j in range(y, y + h):
    #             clone_stocks[best_stock_idx][i][j] = prod_idx
    #     return clone_stocks, clone_prods

    # def lazy_init_heuristic(self, clone_prods, clone_stocks, indices_prods):
    #     best_stock_idx, best_position, best_prod_size = -1, None, [0, 0]
    #     if not hasattr(self, 'sorted_prods'):
    #         self.sorted_prods = sorted(clone_prods, key=lambda p: p["size"][0] * p["size"][1], reverse=True)
    #         self.indices_prods = sorted(self.indices_prods, key=lambda i: clone_prods[i]["size"][0] * clone_prods[i]["size"][1], reverse=True)
    #         # self.sorted_prods = sorted(self.list_products, key=lambda p: (p["size"][0], p["size"][1]), reverse=True)
    #     if not hasattr(self, 'sorted_stocks'):
    #         self.sorted_stocks = sorted(enumerate(clone_stocks), key=lambda x: self._get_stock_size_(x[1])[0] * self._get_stock_size_(x[1])[1])

    #     clone_prods = self.sorted_prods
    #     sorted_stocks = self.sorted_stocks
    #     # print("Sorted first stock: ",self._get_stock_size_(sorted_stocks[0][1]))
    #     # Group stocks into buckets based on size ranges
    #     self._group_stocks_into_buckets(clone_stocks)
    #     # print(clone_prods)
        
    #     for prod_idx,prod in enumerate(clone_prods):
    #         if prod["quantity"] > 0:
    #             prod_size = prod["size"]
    #             min_waste_percentage = float('inf')
    #             candidate_stocks = self._get_candidate_stocks(prod_size)
                
    #             for stock_idx, stock in candidate_stocks:
    #                 placed = False
    #                 position = self._find_position(stock, prod_size[0], prod_size[1])
    #                 if position:
    #                     stock_w, stock_h = self._get_stock_size_(stock)
    #                     stock_area = stock_w * stock_h
    #                     prod_area = prod_size[0] * prod_size[1]
    #                     waste_percentage = (stock_area - prod_area) / stock_area
    #                     if waste_percentage < min_waste_percentage:
    #                         min_waste_percentage = waste_percentage
    #                         best_stock_idx = stock_idx
    #                         best_position = position
    #                         best_prod_size = prod_size
    #                         placed = True
    #                         break
    #             if best_position and best_stock_idx != -1:
    #                 prod["quantity"] -= 1
    #                 return {"prod_idx": self.indices_prods[prod_idx], "stock_idx": best_stock_idx, "size": (best_prod_size[0], best_prod_size[1]), "position": best_position}
    #     return {"stock_idx": -1, "size": [0, 0], "position": None}

    # def _group_stocks_into_buckets(self, stocks):
    #     self.stock_buckets = {}
    #     for idx, stock in enumerate(stocks):
    #         stock_w, stock_h = self._get_stock_size_(stock)
    #         bucket_key = (stock_w // self.bucket_size, stock_h // self.bucket_size)
    #         if bucket_key not in self.stock_buckets:
    #             self.stock_buckets[bucket_key] = []
    #         self.stock_buckets[bucket_key].append((idx, stock))

    # def _get_candidate_stocks(self, prod_size):
    #     prod_w, prod_h = prod_size
    #     bucket_key = (prod_w // self.bucket_size, prod_h // self.bucket_size)
    #     candidate_stocks = []
    #     for key in self.stock_buckets:
    #         if key[0] >= bucket_key[0] and key[1] >= bucket_key[1]:
    #             candidate_stocks.extend(self.stock_buckets[key])
    #     return candidate_stocks

    # def _find_position(self, stock, product_width, product_height):
    #     stock_width, stock_height = self._get_stock_size_(stock)

    #     for x in range(stock_width - product_width + 1):
    #         for y in range(stock_height - product_height + 1):
    #             if self._can_place_(stock, (x, y), (product_width, product_height)):
    #                 return (x, y)
    #     return None
    
    def __init__(self):
        self.optimal_patterns = []
        self.isComputing = True
        self.drawing_counter = -1
        self.drawing_data = []
        self.indices_prods = []
        self.list_stocks = []
        self.list_products = []

    def get_action(self, observation, info):
        if(self.isComputing):
            self.init_heuristic(observation,info)
            self.isComputing = False
            for data in self.optimal_patterns:
                stock_type = data['bin_class_id']
                # stock_idx = self.list_stocks[stock_type]['stock_index'][0]
                # self.list_stocks[stock_type]['stock_index'].pop(0)
            #     if data['quantity'] == 0: continue
            #     for _ in range(data['quantity']):
            #         stock_type = data['stock_type']
            #         stock_idx = self.list_stocks[stock_type]['stock_index'][0]
            #         self.list_stocks[stock_type]['stock_index'].pop(0)
            #         items = data['items']
            #         if items:
            #             for item_id, details in items.items():
            #                 size = (details['width'], details['height'])
            #                 positions = details['positions']
            #                 for position in positions:
            #                     self.drawing_data.append({
            #                         'stock_idx': stock_idx,
            #                         'size': size,
            #                         'position': position,
            #                     })

            self.drawing_counter += 1
            return {
                "stock_idx": self.drawing_data[self.drawing_counter]["stock_idx"],
                "size": self.drawing_data[self.drawing_counter]["size"],
                "position": self.drawing_data[self.drawing_counter]["position"]
            }
        else:
            self.drawing_counter += 1
            return {
                "stock_idx": self.drawing_data[self.drawing_counter]["stock_idx"],
                "size": self.drawing_data[self.drawing_counter]["size"],
                "position": self.drawing_data[self.drawing_counter]["position"]
            }
        
    def init_heuristic(self, observation, info):
        # Student code here
        initial_stocks = copy.deepcopy(observation["stocks"])
        initial_prods = copy.deepcopy(observation["products"])
        # prod_num = 0

        for prod_idx,prod in enumerate(initial_prods):
            prod_info = {'id': str(prod_idx),"width": prod["size"][0], "height": prod["size"][1], "quantity": prod["quantity"]}
            self.list_products.append(prod_info)
            # prod_num += prod["quantity"]
            prod_info = {'id': str(prod_idx) + '_rotated',"width": prod["size"][1], "height": prod["size"][0], "quantity": prod["quantity"]}
            self.list_products.append(prod_info)
        self.list_products.sort(key=lambda x: (-x['height'], -x['width']))

        for stock_i_idx,stock_i in enumerate(initial_stocks):
            stock_w, stock_h = self._get_stock_size_(stock_i)
            duplicated_stock_idx = -1
            for stock_idx,stock in enumerate(self.list_stocks):
                if min(stock_w,stock_h) == stock["width"] and max(stock_h,stock_w) == stock["length"]:
                    duplicated_stock_idx = stock_idx
                    break
            if duplicated_stock_idx != -1:
                self.list_stocks[duplicated_stock_idx]["quantity"] += 1
                self.list_stocks[duplicated_stock_idx]["stock_index"].append(stock_i_idx)
            else:
                stock_info = {'id': stock_i_idx,"width": min(stock_w,stock_h), "length": max(stock_h,stock_w), "quantity": 1, "stock_index": [stock_i_idx], 'used': 0 }
                self.list_stocks.append(stock_info)
        self.list_stocks.sort(key=lambda x:x['width'] * x['length'])

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
                current_bin = {'id': bin_counter, 'bin_class_id': bin_class['id'], 'length': bin_class['length'], 'width': bin_class['width'], 'remaining_length': bin_class['length'], 'remaining_width': bin_class['width'], 'strips': []}
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

                    # item_placement = ItemPlacement(
                    #     item_class_id=item.id,
                    #     quantity=items_to_place,
                    #     position=(0, current_bin.length - current_bin.remaining_length)
                    # )
                    item_placement = {'item_class_id': item['id'], 'quantity': items_to_place}
                    # strip = Strip(
                    #     width=strip_width,
                    #     height=strip_height,
                    #     items=[item_placement]
                    # )
                    strip = {'length': strip_length, 'width': strip_width, 'item': [item_placement]}

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
                    # fill_strip_with_smaller_items(
                    #     strip,
                    #     list_products,
                    #     item_demand,
                    #     current_bin
                    # )
                    
                    strip_remaining_length = current_bin['length'] - strip['length']
                    if strip_remaining_length > 0:
                        for next_item in self.list_products:
                            if item_demand[next_item['id']] > 0 and next_item['width'] <= strip_remaining_length and next_item['height'] <= strip_width:
                                items_to_place = min(item_demand[next_item['id']],int(strip_remaining_length // next_item['width']))
                                if(items_to_place > 0):
                                    item_placement = {'item_class_id': next_item['id'], 'quantity': items_to_place}
                                    strip['item'].append(item_placement)
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

                            # item_placement = ItemPlacement(
                            #     item_class_id=item.id,
                            #     quantity=items_to_place,
                            #     position=(0, current_bin.length - current_bin.remaining_length)
                            # )
                            item_placement = {'item_class_id': sub_item['id'], 'quantity': items_to_place}
                            # strip = Strip(
                            #     width=strip_width,
                            #     height=strip_height,
                            #     items=[item_placement]
                            # )
                            strip = {'length': strip_length, 'width': strip_width, 'item': [item_placement]}

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
                                            item_placement = {'item_class_id': next_item['id'], 'quantity': items_to_place}
                                            strip['item'].append(item_placement)
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

        self.optimal_patterns = initial_patterns

        for pattern in self.optimal_patterns:
            print(pattern)

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

    # def get_action(self, observation, info):
    #     list_prods = observation["products"]
    #     best_stock_idx, best_position, best_prod_size = -1, None, [0, 0]
    #     if not hasattr(self, 'sorted_prods'):
    #         self.sorted_prods = sorted(list_prods, key=lambda p: p["size"][0] * p["size"][1], reverse=True)
    #         # self.sorted_prods = sorted(list_prods, key=lambda p: (p["size"][0], p["size"][1]), reverse=True)
    #     if not hasattr(self, 'sorted_stocks'):
    #         self.sorted_stocks = sorted(enumerate(observation["stocks"]), key=lambda x: self._get_stock_size_(x[1])[0] * self._get_stock_size_(x[1])[1])
    #     list_prods = self.sorted_prods
    #     sorted_stocks = self.sorted_stocks
    #     # Group stocks into buckets based on size ranges
    #     self._group_stocks_into_buckets(observation["stocks"])
        
    #     for prod in list_prods:
    #         if prod["quantity"] > 0:
    #             prod_size = prod["size"]
    #             min_waste_percentage = float('inf')
    #             candidate_stocks = self._get_candidate_stocks(prod_size)
                
    #             for stock_idx, stock in candidate_stocks:
    #                 placed = False
    #                 position = self._find_position(stock, prod_size[0], prod_size[1])
    #                 if position:
    #                     stock_w, stock_h = self._get_stock_size_(stock)
    #                     stock_area = stock_w * stock_h
    #                     prod_area = prod_size[0] * prod_size[1]
    #                     waste_percentage = (stock_area - prod_area) / stock_area
    #                     if waste_percentage < min_waste_percentage:
    #                         min_waste_percentage = waste_percentage
    #                         best_stock_idx = stock_idx
    #                         best_position = position
    #                         best_prod_size = prod_size
    #                         placed = True
    #                         break
    #             if best_position and best_stock_idx != -1:
    #                 return {"stock_idx": best_stock_idx, "size": (best_prod_size[0], best_prod_size[1]), "position": best_position}
    #     return {"stock_idx": -1, "size": [0, 0], "position": None}
    # def _group_stocks_into_buckets(self, stocks):
    #     self.stock_buckets = {}
    #     for idx, stock in enumerate(stocks):
    #         stock_w, stock_h = self._get_stock_size_(stock)
    #         bucket_key = (stock_w // self.bucket_size, stock_h // self.bucket_size)
    #         if bucket_key not in self.stock_buckets:
    #             self.stock_buckets[bucket_key] = []
    #         self.stock_buckets[bucket_key].append((idx, stock))
    # def _get_candidate_stocks(self, prod_size):
    #     prod_w, prod_h = prod_size
    #     bucket_key = (prod_w // self.bucket_size, prod_h // self.bucket_size)
    #     candidate_stocks = []
    #     for key in self.stock_buckets:
    #         if key[0] >= bucket_key[0] and key[1] >= bucket_key[1]:
    #             candidate_stocks.extend(self.stock_buckets[key])
    #     return candidate_stocks
    # def _find_position(self, stock, product_width, product_height):
    #     stock_width, stock_height = self._get_stock_size_(stock)
    #     for x in range(stock_width - product_width + 1):
    #         for y in range(stock_height - product_height + 1):
    #             if self._can_place_(stock, (x, y), (product_width, product_height)):
    #                 return (x, y)
    #     return None
    # def _place_product(self, stock, product_width, product_height, position):
    #     if position is None:
    #         return  # No valid position found, do nothing
    #     x, y = position
    #     stock_width, stock_height = self._get_stock_size_(stock)
    #     # Ensure the product is placed within the stock dimensions
    #     # if x + product_width > stock_width or y + product_height > stock_height:
    #     #     return
    #     for i in range(product_height):
    #         for j in range(product_width):
    #             stock[y + i][x + j] = 1  # Mark the stock as used

    # You can add more functions if needed
