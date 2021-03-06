import spotipy
import json
import os
import random


data_dir = os.path.join(os.getcwd(),'json_files')
users_file = os.path.join(data_dir,'all_user_data.json')

class SongSpotting:

	def __init__(self,access_token):
		self.sp = spotipy.Spotify(auth=access_token)
		self.playlist_name = "SongSpotting - Daily Playlist"
		self.u_id = self.sp.current_user()['id'] 


	def store_token(self,token_data):
		
		file = os.path.join(data_dir,'{0}_token.json'.format(self.u_id))
		with open(file, 'w') as f:
			json.dump(token_data,f)
		return

	def get_all_user_data(self):

		with open(users_file,'r') as f:
			all_user_data = json.load(f)

		return all_user_data

	def store_all_user_data(self,all_user_data):

		with open(users_file,'w') as f:
			json.dump(all_user_data,f)
		return


	def get_all_users(self):
		
		all_user_data = self.get_all_user_data()
		user_ids = [user['u_id'] for user in all_user_data]
		return user_ids	


	def get_seed_tracks(self):

		top_tracks = self.sp.current_user_top_tracks(limit=50, time_range='short_term')
		top_track_ids = [track['id'] for track in top_tracks['items']]

		if len(top_track_ids) >= 5:
			seed = random.sample(top_track_ids,5)
		else:
			seed = top_track_ids
		return seed


	def get_recommendations(self,seed):
		
		recommended_tracks = self.sp.recommendations(seed_tracks=seed,limit=20)
		recommended_track_ids = [track['id'] for track in recommended_tracks['tracks']]

		return recommended_track_ids


	def store_user(self,p_id):

		user_data = {'u_id':self.u_id,'p_id':p_id}
		all_user_data = self.get_all_user_data()
		all_user_data.append(user_data)
		self.store_all_user_data(all_user_data)
		
		return

	def setup_user(self):

		p_id = self.sp.user_playlist_create(self.u_id,self.playlist_name)['id']
		self.store_user(p_id)

		seed = self.get_seed_tracks()
		recommendations = self.get_recommendations(seed)
		self.sp.user_playlist_replace_tracks(self.u_id,p_id,recommendations)

		return p_id


	def get_user_playlist_ids(self,limit=50,offset=0):
		
		playlists = self.sp.current_user_playlists(limit=limit,offset=offset)
		playlist_ids = [pl['id'] for pl in playlists['items']]

		#Max returned ids per call is 50.
		#The offset serves as an index, so if the total is higher than 
		#the limit, we can offset the index and query the remaining records
		while len(playlist_ids) < playlists['total']:
			offset+=limit
			playlists = self.sp.current_user_playlists(limit=limit,offset=offset)
			playlist_ids.extend([pl['id'] for pl in playlists['items']])

		return playlist_ids


	def get_user_ss_playlist_id(self):

		all_user_data = self.get_all_user_data()

		playlist_ids = [user['p_id'] for user in all_user_data if user['u_id'] == self.u_id]
		p_id = playlist_ids[0] if len(playlist_ids) > 0 else None
		return p_id

	def delete_user(self):

		all_user_data = self.get_all_user_data()
		all_user_data = [user for user in all_user_data if user['u_id'] != self.u_id]
		self.store_all_user_data(all_user_data)

		return

	def refresh_playlist(self,playlist_id):

		seed = self.get_seed_tracks()
		recommendations = self.get_recommendations(seed)
		self.sp.user_playlist_replace_tracks(self.u_id,playlist_id,recommendations)
