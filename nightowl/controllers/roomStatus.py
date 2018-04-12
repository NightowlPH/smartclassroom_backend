from flask import Flask, redirect, url_for, request,render_template,flash
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import token_required
from flask_restful import Resource

from nightowl.models.roomStatus import RoomStatus


class roomStatus(Resource):
	def get(self):
		return {'hello': 'world'}