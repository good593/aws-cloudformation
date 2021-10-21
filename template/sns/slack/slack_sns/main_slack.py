import datetime, os, copy, json, zlib, logging

from base64 import b64decode
from slack_sdk import WebClient
from slack_constants import SLACK_BLOCK_TYPE

__all__ = ["AICO_SLACK", "AWS_LOG"]

class AWS_LOG:

	def __init__(self, pEvent: dict):
		self.log_data = pEvent
		self.product_cd = "상품 코드" + " / " + "상태 코드"
		self.slack_channel_nm = "슬렉 체널명"
		self.default_log_link = "https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups".format(
			region=os.environ.get('DEFAULT_REGION', 'ap-northeast-2'))
		self.service_info = None

	def __aws_decode(self, pLogData: str) -> dict:
		''' aws log decode '''
		compressed_payload = b64decode(pLogData)
		json_payload = zlib.decompress(compressed_payload, 16+zlib.MAX_WBITS)
		return json.loads(json_payload)

	def __revert_url_cd(self, pUrlCd: str) -> str:
		return pUrlCd.replace('$','$2524').replace('/','$252F').replace('[','$255B').replace(']','$255D')

	def __make_cloudwatch_url(self, pLogGroup: str,pLogEvent: str) -> str:
		'''cloud watch pretty log'''
		encoded_log_group=self.__revert_url_cd(pLogGroup)
		encoded_log_event=self.__revert_url_cd(pLogEvent)

		return self.default_log_link+"/log-group/{log_name}/log-events/{events}".format( 
			log_name=encoded_log_group,
			events=encoded_log_event)

	def __utc_to_kst(self, pDt: datetime):
		# +9 (kst)
		hours_added = datetime.timedelta(hours = 9)

		return (pDt + hours_added).strftime('%Y-%m-%d %H:%M:%S KST')

	def __revert_subscription_filter_log(self, pLogData: str):
		"""error event에서 원하는 파라미터만 추출"""
		log_data = self.__aws_decode(pLogData)

		log_group = log_data['logGroup']
		log_stream = log_data['logStream']
		log_dt = self.__utc_to_kst(datetime.datetime.fromtimestamp(log_data['logEvents'][0]['timestamp']/1000)) 
		error_message= '' #logEvents['message'].split('\n')[0]
		for logEvent in log_data['logEvents']:
			error_message += logEvent['message'] #+'\n'

			try:
				log_message = logEvent['message'].replace('\\', '')
				logging.debug("log_message : "+log_message)
				if log_message.find('slack_channel_nm') > 0 \
					and log_message.find('{"product_cd"') > 0:
					from_idx = log_message.find('{"product_cd"')
					end_idx = -1
					if log_message.find('","errorType"') > 0:
						end_idx = log_message.find('","errorType"')
					elif log_message.find('Traceback') > 0:
						end_idx = log_message.find('Traceback')
					aico_base_error_msg = json.loads(log_message[from_idx:end_idx])
					
					self.product_cd = aico_base_error_msg['product_cd']
					self.slack_channel_nm = aico_base_error_msg['slack_channel_nm']
					if 'service_info' in aico_base_error_msg.keys():
						self.service_info = aico_base_error_msg['service_info']
			except ValueError as e:
				continue

		logs_link = self.__make_cloudwatch_url(log_group,log_stream)
		
		return log_group,error_message,log_dt,logs_link

	def __revert_alarm_log(self, pLogDict: dict):
		service_nm = pLogDict['Subject']
		log_dt = self.__utc_to_kst(datetime.datetime.strptime(pLogDict['Timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')) 
		error_msg = pLogDict['Message']

		return service_nm, log_dt, error_msg

	def get_slack_msgs(self):
		slack_msgs = []
		
		if 'awslogs' in self.log_data and 'data' in self.log_data['awslogs']:
			slack_msg = {}
			log_group,error_message,log_dt,logs_link = self.__revert_subscription_filter_log(self.log_data["awslogs"]["data"])
			
			slack_msg['ERROR_MSG'] = error_message #json.dumps(event, ensure_ascii=False)
			slack_msg['MSG_LINK'] = logs_link
			slack_msg['ERROR_TIME'] = log_dt
			slack_msg['PRODUCT_CODE'] = self.product_cd

			if os.environ.get('SERVICE_NM', None):
				slack_msg['SERVICE_NM'] = os.environ['SERVICE_NM']
			else:
				slack_msg['SERVICE_NM'] = log_group
				
			if self.service_info:
				slack_msg['SERVICE_INFO'] = self.service_info
				#초기화
				self.service_info = None

			slack_msgs.append(slack_msg)

		elif 'Records' in self.log_data and isinstance(self.log_data['Records'], type([])):
			for record in self.log_data['Records']:
				if 'Sns' in record:
					slack_msg = {}
					service_nm, log_dt, error_msg = self.__revert_alarm_log(record['Sns'])
					
					slack_msg['ERROR_MSG'] = error_msg #json.dumps(event, ensure_ascii=False)
					slack_msg['MSG_LINK'] = self.default_log_link
					slack_msg['ERROR_TIME'] = log_dt
					slack_msg['PRODUCT_CODE'] = self.product_cd
					slack_msg['SERVICE_NM'] = service_nm

					slack_msgs.append(slack_msg)
		else:
			logging.error('[AWS_LOG][get_slack_msgs] No Log Data')
		
		return slack_msgs

class AICO_SLACK:
	def __init__(self, pSlackChannelNm: str):
		self.slack_channel = pSlackChannelNm
		self.client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN', 'xoxb-1937774451878-1941506985429-IklWAs8FFZwk6rLD6s0gQOpO')) 
		self.format_msg = {
			"ERROR_MSG": None,
			"ERROR_TIME": None,
			"MSG_LINK": None,
			"PRODUCT_CODE": None,
			"SERVICE_NM": None,
		}
	
	def __init_blocks(self, pMsg: dict) -> list:
		#Header > Occurred at
		p_header = copy.deepcopy(SLACK_BLOCK_TYPE.HEADER.value[2])
		p_header['text']['text'] = p_header['text']['text'].replace("{SERVICE_NM}", pMsg["SERVICE_NM"])
		return [
			copy.deepcopy(SLACK_BLOCK_TYPE.DIVIDER.value[2]),
			p_header
		]

	def __post_message(self, pBlocks: list, pThreadTs: str = None) -> dict:
		result = None
		if pThreadTs is None:
			result = self.client.chat_postMessage(
				channel=self.slack_channel.value[2], blocks=pBlocks
			)
		else:
			result = self.client.chat_postMessage(
				channel=self.slack_channel.value[2], thread_ts=pThreadTs, blocks=pBlocks
			)

		return result

	def __check_pre_message_by_today(self, pMsg: dict) -> str:

		thread_ts = None
		history = self.client.conversations_history(channel=self.slack_channel.value[2])["messages"]
		today_dt = datetime.date.today().strftime("%Y%m%d")
		is_breake = False

		for msg in history:
			if is_breake:
				break
			
			try:
				msg_dt = datetime.datetime.fromtimestamp(float(msg["latest_reply"])).strftime("%Y%m%d")
				if msg_dt == today_dt:
					for block in msg["blocks"]:
						try:  
							if "header" == block["type"] and pMsg["SERVICE_NM"] in block["text"]["text"]:
								thread_ts = msg["ts"]
								is_breake = True
								break
						except KeyError as e:
							logging.error(e)
							continue
			except KeyError as e:
				logging.error(e)
				continue
		
		if thread_ts is None:
			blocks = self.__init_blocks(pMsg)
			thread_ts = self.__post_message(pBlocks=blocks)["ts"]

		return thread_ts

	def get_format_msg(self) -> dict:
		return self.format_msg

	def do_message(self, pMsg: dict, pSendThred: bool=True) -> bool:
		blocks = self.__init_blocks(pMsg)
		# 쓰레드 메세지 사용유무
		thread_ts = None
		if self.slack_channel.value[3] and pSendThred:
			thread_ts = self.__check_pre_message_by_today(pMsg)
			blocks = [	blocks[0]	]
		elif self.slack_channel.value[3]:
			self.__check_pre_message_by_today(pMsg)
			return None

		#Section > Product Code, Occurred time
		p_st = copy.deepcopy(SLACK_BLOCK_TYPE.SECTION.value[2])
		if 'PRODUCT_CODE' in pMsg.keys():
			p_st['fields'][0]['text'] = p_st['fields'][0]['text'].replace("{PRODUCT_CODE}", pMsg["PRODUCT_CODE"])
		else:
			p_st['fields'][0]['text'] = p_st['fields'][0]['text'].replace("{PRODUCT_CODE}", PRODUCT_CODE.none.name)

		if 'MSG_LINK' in pMsg.keys():
			p_st['fields'][1]['text'] = p_st['fields'][1]['text'].replace("{ERROR_TIME}", pMsg["ERROR_TIME"])
		else:
			del p_st['fields'][1]
		blocks.append(p_st)
		#Button > Link to details
		if 'MSG_LINK' in pMsg.keys():
			p_bt = copy.deepcopy(SLACK_BLOCK_TYPE.BUTTON.value[2])
			p_bt['accessory']['url'] = p_bt['accessory']['url'].replace("{MSG_LINK}", pMsg["MSG_LINK"])
			blocks.append(p_bt)
		#Message > service info
		if 'SERVICE_INFO' in pMsg.keys():
			p_msg = copy.deepcopy(SLACK_BLOCK_TYPE.MESSAGE.value[2])
			p_msg['text']['text'] = p_msg['text']['text'].replace("{MESSAGE}", "*SERVICE_INFO:*\n"+json.dumps(pMsg["SERVICE_INFO"], ensure_ascii=False))
			blocks.append(p_msg)
		#Message > Error Message
		if 'ERROR_MSG' in pMsg.keys():
			p_msg = copy.deepcopy(SLACK_BLOCK_TYPE.MESSAGE.value[2])
			p_msg['text']['text'] = p_msg['text']['text'].replace("{MESSAGE}", "*Reason:*")
			blocks.append(p_msg)
			p_error_msg = copy.deepcopy(SLACK_BLOCK_TYPE.ERROR_MESSAGE.value[2])
			p_error_msg['elements'][0]['text'] = p_error_msg['elements'][0]['text'].replace("{ERROR_MSG}", pMsg["ERROR_MSG"])
			blocks.append(p_error_msg)

		return self.__post_message(pBlocks=blocks, pThreadTs=thread_ts)["ok"]


