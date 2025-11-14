#!/usr/bin/env python3
"""Create AWS CodeBuild and CodePipeline for ULTRON Agent"""

import boto3
import json
from pathlib import Path

def create_codebuild_project():
    """Create CodeBuild project"""
    codebuild = boto3.client('codebuild', region_name='us-east-1')
    
    project_config = {
        'name': 'ultron-agent-build',
        'description': 'ULTRON Agent CI/CD Build Project',
        'source': {
            'type': 'GITHUB',
            'location': 'https://github.com/dqikfox/ultron_agent.git',
            'buildspec': 'aws_integration/codebuild/buildspec.yml'
        },
        'artifacts': {
            'type': 'S3',
            'location': 'ultron-agent-pipeline-artifacts'
        },
        'environment': {
            'type': 'LINUX_CONTAINER',
            'image': 'aws/codebuild/amazonlinux2-x86_64-standard:3.0',
            'computeType': 'BUILD_GENERAL1_SMALL'
        },
        'serviceRole': 'arn:aws:iam::941284019015:role/service-role/codebuild-ultron-agent-service-role'
    }
    
    try:
        response = codebuild.create_project(**project_config)
        print(f"CodeBuild project created: {response['project']['name']}")
        return True
    except Exception as e:
        print(f"CodeBuild creation failed: {e}")
        return False

def create_codepipeline():
    """Create CodePipeline"""
    codepipeline = boto3.client('codepipeline', region_name='us-east-1')
    
    pipeline_path = Path('aws_integration/codepipeline/pipeline.json')
    with open(pipeline_path) as f:
        pipeline_config = json.load(f)
    
    try:
        response = codepipeline.create_pipeline(**pipeline_config)
        print(f"CodePipeline created: {response['pipeline']['name']}")
        return True
    except Exception as e:
        print(f"CodePipeline creation failed: {e}")
        return False

def main():
    print("Creating AWS CodeBuild and CodePipeline for ULTRON Agent")
    
    # Create CodeBuild project
    if create_codebuild_project():
        print("✅ CodeBuild project created")
    else:
        print("❌ CodeBuild project creation failed")
    
    # Create CodePipeline
    if create_codepipeline():
        print("✅ CodePipeline created")
    else:
        print("❌ CodePipeline creation failed")

if __name__ == "__main__":
    main()